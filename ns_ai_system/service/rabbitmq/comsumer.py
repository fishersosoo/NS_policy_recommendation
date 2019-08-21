# coding=utf-8
import json
import multiprocessing
import time

import pika
import pika.exceptions

from celery_task.policy.tasks import check_single_guide
from data_management.api.rpc_proxy import rpc_server
from data_management.config import py_client
from service.base_func import is_expired, need_to_update_guides
from service.rabbitmq.rabbit_mq import connect_channel


def create_task(ch, company_id, guide_id, routing_key):
    """

    Args:
        task:
        ch:

    Returns:

    """
    # TODO:这里存到数据库，方便调试
    MAX_LEN = 100
    RETRY_AFTER = 0.1
    MAX_RETRY_TIME = 5
    while True:
        if rpc_server().rabbitmq.get_message_count("check_single_guide").get("result",0) <= MAX_LEN:
            check_single_guide.delay(company_id, guide_id, routing_key)
            return
        else:
            time.sleep(RETRY_AFTER)
            RETRY_AFTER *= 2
            if RETRY_AFTER >= MAX_RETRY_TIME:
                RETRY_AFTER = MAX_RETRY_TIME


def single_guide_callback(ch, method, properties, body):
    input = json.loads(body)
    # 检查是否过期
    recommend_record = py_client.ai_system["recommend_record"].find_one(
        {"company_id": input["company_id"], "guide_id": input["guide_id"]})
    if recommend_record is None or is_expired(recommend_record):
        # 阻塞直到任务队列有空位
        create_task(ch, input["company_id"], input["guide_id"], routing_key="task.single.output")
    else:
        rpc_server().rabbitmq.push_message("task", "task.single.output",
                                         {"company_id": input["company_id"], "guide_id": input["guide_id"],
                                          "score": recommend_record["score"]}, channel=ch)


def multi_guide_callback(ch, method, properties, body):
    """
    注意，只有经过计算的结果才会放到结果队列中，对于那些没有过期的任务将不会放到结果队列
    Args:
        ch:
        method:
        properties:
        body:

    Returns:

    """
    # 获取需要计算的企业id
    input = json.loads(body)
    for guide_id in need_to_update_guides(input["company_id"]):
        create_task(ch, input["company_id"], guide_id, routing_key="task.multi.output")


def start_consuming(callback, queue):
    """
    将一个回调函数绑定在一个队列上
    Args:
        callback: 回调函数
        queue: 队列名称

    Returns:

    """
    print("start_consuming")
    time.sleep(3)
    channel, connect = None, None
    while True:
        connect, channel = connect_channel(connect, channel)
        channel.basic_consume(queue, callback, auto_ack=True)
        try:
            channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            continue
            # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:
            print("Caught a channel error: {}, stopping...".format(err))
            break
            # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            print("Connection was closed, retrying...")
            continue


def kill_processes(processes):
    print("stop_consuming")

    for p in processes:
        p.terminate()


def create_consum_process():
    """
    创建进程
    Returns:

    """
    # TODO:需要监控进程
    processes = [multiprocessing.Process(target=start_consuming, args=(single_guide_callback, "single_guide_task")),
                 multiprocessing.Process(target=start_consuming, args=(multi_guide_callback, "multi_guide_task"))]
    for p in processes:
        p.start()
    import atexit

    atexit.register(kill_processes, processes)
