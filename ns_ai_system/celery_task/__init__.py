# coding=utf-8
from celery import Celery
from celery.signals import after_setup_logger
from celery.utils.log import get_task_logger

from celery_task.comsumer import create_consum_process
from my_log import Loggers
import logging

from read_config import config
from kombu import Queue

from service import connect_channel

celery_app = Celery('ns_ai_system',
                    broker=config.get('celery', 'broker'))
celery_app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_RESULT_BACKEND=f'mongodb://{config.get("mongoDB","host")}:{config.get("mongoDB","port")}/celery',
    CELERY_RESULT_BACKEND_SETTINGS={
        "host": config.get("mongoDB", "host"),
        "port": int(config.get("mongoDB", "port")),
        "database": config.get("celery", "backend"),
        "taskmeta_collection": "stock_taskmeta_collection",
    },
)
celery_app.conf.CELERY_DEFAULT_QUEUE = 'default'
celery_app.conf.CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('understand', routing_key='understand'),
    Queue('batch_check_callback', routing_key="batch_check_callback"),
    Queue('check_single_guide', routing_key="check_single_guide"),
    Queue('recommend_task', routing_key="celery_task.policy.tasks.recommend_task")
)
celery_app.conf.CELERY_ROUTES = {
    'celery_task.policy.tasks.understand_guide_task': {'queue': 'understand'},
    'celery_task.policy.tasks.check_single_guide_batch_companies': {'queue': 'batch_check_callback'},
    'celery_task.policy.tasks.push_single_guide_result': {'queue': 'batch_check_callback'},
    'celery_task.policy.tasks.check_single_guide': {'queue': 'check_single_guide'},
    'celery_task.policy.tasks.recommend_task': {'queue': 'recommend_task'},
}

channel = connect_channel()

create_consum_process()
log = get_task_logger(__name__)


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    Loggers.init_app('celery', logger)
    logger.setLevel(logging.INFO)


from celery_task.policy import *
