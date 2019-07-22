# coding=utf-8
import json
import multiprocessing

import time
import pika
import pika.exceptions

from celery_task.policy.tasks import _check_single_guide, check_single_guide
from data_management.config import py_client
from read_config import config
from service import connect_channel
from service.base_func import is_expired, need_to_update_guides


def get_message_count(ch, queue):
    """
    检查队列里面的消息
    Args:
        queue: 队列名称
        ch:

    Returns:

    """
    while True:
        try:
            queue = ch.queue_declare(
                queue=queue, passive=True
            )
            return queue.method.message_count
        except pika.exceptions.ConnectionClosedByBroker:
            ch = connect_channel()
            continue
            # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:
            print("Caught a channel error: {}, stopping...".format(err))
            break
            # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            ch = connect_channel()
            print("Connection was closed, retrying...")
            continue


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
        if get_message_count(ch, "check_single_guide") <= MAX_LEN:
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
    if is_expired(recommend_record):
        # 阻塞直到任务队列有空位
        create_task(ch, input["company_id"], input["guide_id"], routing_key="task.single.output")


def multi_guide_callback(ch, method, properties, body):
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
    while True:
        channel = connect_channel()
        channel.basic_consume(queue, callback)
        try:
            channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            # Uncomment this to make the example not attempt recovery
            # from server-initiated connection closure, including
            # when the node is stopped cleanly
            #
            # break
            continue
            # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:
            print("Caught a channel error: {}, stopping...".format(err))
            break
            # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            print("Connection was closed, retrying...")
            continue


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
