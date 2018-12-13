# coding=utf-8
from celery_task import celery
from data_management.config import mongodb
from data_management.models import UUID
from service.policy_graph_construct import understand_guide


@celery.task
def understand_guide_task(guide_id):
    understand_guide(guide_id)


@celery.task
def recommend_task(company_id):
    import random, datetime
    for one in range(5):
        mongodb["recommend_record"].insert_one(dict(company_id=company_id,
                                                    guide_id=UUID(),
                                                    reason="reason1",
                                                    matching=random.random(),
                                                    time=datetime.datetime.now(),
                                                    latest=True
                                                    ))
    return company_id
