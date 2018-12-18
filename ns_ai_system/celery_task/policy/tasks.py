# coding=utf-8
import datetime

from celery import group

from celery_task import celery
from data_management.config import mongodb
from data_management.models.guide import Guide
from data_management.models.requirement import Requirement
from service.policy_graph_construct import understand_guide


@celery.task
def understand_guide_task(guide_id):
    """

    :param guide_id: 指南的外部id
    :return:
    """
    understand_guide(guide_id)


@celery.task
def check_single_guide(company_id, guide_node, threshold=.0):
    """
    检查单个指南和企业的匹配信息，如果存在匹配则存放到数据库中
    :param company_id:企业id
    :param guide_node:指南节点
    :return:
    """
    requirements = Guide.find_leaf_requirement(guide_node["id"])
    reasons = []
    for requirement in requirements:
        match, reason = check_single_requirement(company_id, requirement)
        if match:
            reasons.append(reason)
    matching = len(reasons) / len(requirements)
    reasons = "\n".join(reasons)
    mongodb["recommend_record"].update({"company_id": company_id, "guide_id": guide_node["guide_id"]},
                                       {"$set": {"latest": False}})
    mongodb["recommend_record"].insert_one(dict(company_id=company_id,
                                                guide_id=guide_node["guide_id"],
                                                reason=reasons,
                                                matching=matching,
                                                time=datetime.datetime.now(),
                                                latest=True
                                                ))


def check_single_requirement(company_id, requirement_node):
    """
    检查企业是否满足单一条件
    :param company_id: 企业id
    :param requirement_node: 条件节点
    :return: match, reason. match表示是否满足，reason，如果不满足则原因为None
    """
    subject_node, predictate_node, object_node = Requirement.get_triple(requirement_node["id"])
    reason = None
    return True, reason


@celery.task
def recommend_task(company_id, threshold=.0):
    """
    更新指定企业的推荐记录
    :param company_id: 企业id
    :param threshold: 匹配度阈值（尚未使用），只有企业与指南匹配度高于此值时候才会推荐
    :return:
    """
    # guides = Guide.list_valid_guides()
    # task_group = group([check_single_guide.s(company_id, guide) for guide in guides])
    # 异步执行
    # result = job.apply_async()
    # 同步执行
    # result = task_group().get()
    return {"company_id": company_id, "latest_id": []}
