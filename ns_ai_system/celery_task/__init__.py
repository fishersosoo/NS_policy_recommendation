# coding=utf-8
from celery import Celery
from celery.utils.log import get_task_logger

from read_config import ConfigLoader

config = ConfigLoader()

celery_app = Celery('ns_ai_system',
                    broker=config.get('celery', 'broker'))
celery_app.conf.update(
    CELERYD_CONCURRENCY=12,
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

log = get_task_logger(__name__)

from celery_task.policy import *
