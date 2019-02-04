# coding=utf-8
from celery import Celery
from celery.utils.log import get_task_logger

celery_app = Celery('ns_ai_system',
                    broker='redis://127.0.0.1:8000/0',
                    backend='mongodb://ns.fishersosoo.xyz:80/celery')
celery_app.conf.update(
    CELERYD_CONCURRENCY=10,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_RESULT_BACKEND='mongodb://ns.fishersosoo.xyz:80/celery',
    CELERY_RESULT_BACKEND_SETTINGS={
        "host": "ns.fishersosoo.xyz",
        "port": 80,
        "database": "celery",
        "taskmeta_collection": "stock_taskmeta_collection",
    },
)

log = get_task_logger(__name__)

from celery_task.policy import *
