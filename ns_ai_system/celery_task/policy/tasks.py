# coding=utf-8
import datetime

from celery_task import celery, log
from data_management.config import dataService, py_client
from data_management.models.guide import Guide
from data_management.models.requirement import Requirement
from data_management.models.word import Word
from service.field_match import field_matcher
from service.policy_graph_construct import understand_guide


@celery.task
def understand_guide_task(guide_id):
    """

    :param guide_id: 指南的外部id
    :return:
    """
    understand_guide(guide_id)


@celery.task
def check_single_guide(company_id, guide_id, threshold=.0):
    """
    检查单个指南和企业的匹配信息，如果存在匹配则存放到数据库中
    :param company_id:企业id
    :param guide_id:指南的平台id
    :return:
    """
    _, _, guide_node = Guide.find_by_guide_id(guide_id)
    assert guide_node is not None
    requirements = Guide.find_leaf_requirement(guide_node["id"])
    count = 0
    reasons = []
    base_info = query_data(company_id)
    if base_info is None:
        raise Exception(f"Query data fail for company: {company_id}")
    for leaf in requirements:
        requirement = leaf["leaf"]
        match, reason = check_single_requirement(company_id, requirement)
        if match is None:
            # 忽略条件
            continue
        else:
            count += 1
        if match:
            reasons.append(f'{len(reasons)+1}. {reason}')
    count = 1 if count == 0 else count
    matching = len(reasons) / count
    reasons = "\n".join(reasons)
    reasons = f"企业满足以下条件：【括号中内容为企业的真实情况】\n{reasons}"
    py_client.ai_system["recommend_record"].update({"company_id": company_id,
                                                    "guide_id": guide_id},
                                                   {"$set": {"latest": False}}, upsert=False, multi=True)
    py_client.ai_system["recommend_record"].insert_one(dict(company_id=company_id,
                                                            guide_id=guide_node["guide_id"],
                                                            reason=reasons,
                                                            matching=matching,
                                                            time=datetime.datetime.now(),
                                                            latest=True
                                                            ))
    return dict(company_id=company_id,
                guide_id=guide_node["guide_id"],
                reason=reasons,
                matching=matching,
                time=datetime.datetime.now(),
                latest=True
                )


def check_single_requirement(company_id, requirement_node,base_info):
    """
    检查企业是否满足单一条件
    :param company_id: 企业id
    :param requirement_node: 条件节点
    :return: match, reason. match表示是否满足，reason，如果不满足则原因为None
    """
    subject_node, predicate_node, object_node = Requirement.get_triple(requirement_node["id"])
    subject = dict(subject_node)
    predicate = dict(predicate_node)
    object = dict(object_node)
    requirement_for = subject.get("for", "company")
    if requirement_for != "company":
        # 只处理对企业的要求
        return None, None
    field_info = field_lookup(subject, predicate, object)
    if field_info is None:
        # 只处理对企业的要求
        return None, None

    return field_matcher.is_match(field_info=field_info, query_data=base_info,
                                  spo=[subject, predicate, object])


def infer_field_info_from_object_type(object):
    """
    从object推断字段信息
    :param object:
    :return:
    """
    if object.get("type", None) == "location":
        return {'name': "地址", 'field': "DOM"}
    if object.get("type", None) == "qualification":
        return {'name': "企业资质", 'field': "FQZ_ZZMC"}
    if object.get("type", None) == "scope":
        return {'name': "经营业务范围", 'field': "OPSCOPE"}
    if object.get("type", None) == "industry":
        return {'name': "行业领域", 'field': "INDUSTRY"}
    # TODO:log推断失败
    log.info(f"无法从obejct推断字段信息{object}")
    return None


def field_lookup(subject, predicate, object):
    """

    :return: field_info: {'name':中文名, 'field':字段名}
    """
    # subject上有字段信息
    if subject.get("type", None) == "field":
        field_info = Word.get_field(entity_name=subject["tag"])
        if field_info is not None:
            return field_info
        else:
            # TODO:log 字段匹配失败
            log.info(f"找不到对应字段\n:{subject}")
            return None
    if object.get("type", None) == "field":
        field_info = Word.get_field(entity_name=object["tag"])
        if field_info is not None:
            return field_info
        else:
            # TODO:log 字段匹配失败
            log.info(f"找不到对应字段\n:{object}")
            return None
    if object.get("type", None) == "event" or subject.get("type", None) == "event":
        log.info("事件条件不处理")
        return None
    # subject 上没有字段信息。需要根据object类型推断
    field_info = infer_field_info_from_object_type(object)
    return field_info


def query_data(company_id):
    # get data
    value = dataService.sendRequest("getEntByKeyword", {"keyword": company_id, "type": 1})
    try:
        company_name = value["RESULTDATA"][0]["ENTNAME"]
    except Exception as e:
        log.error(value)
        return None
    # get base info
    base_info = dataService.sendRequest("getRegisterInfo", {"entName": company_name})["RESULTDATA"][0]
    # get qualify
    qualify_certify_count = \
        dataService.sendRequest("getQualifyCertifyInfo", {"entName": company_name, 'pageNo': 1, "pageSize": 1})[
            "PAGEINFO"][
            "TOTAL_COUNT"]
    qualifies = \
        dataService.sendRequest("getQualifyCertifyInfo",
                                {"entName": company_name, 'pageNo': 1, "pageSize": qualify_certify_count})["RESULTDATA"]
    base_info["FQZ_ZZMC"] = [one["FQZ_ZZMC"] for one in qualifies]
    return base_info


@celery.task
def recommend_task(company_id, threshold=.0):
    """
    更新指定企业的推荐记录
    :param company_id: 企业id
    :param threshold: 匹配度阈值（尚未使用），只有企业与指南匹配度高于此值时候才会推荐
    :return:
    """
    log.info(f"recommend_task for company: {company_id}")
    guides = Guide.list_valid_guides()
    results = []
    for guide in guides:
        result = check_single_guide(company_id, guide["guide_id"])
        results.append(result)
    # task_group = group([check_single_guide.s(company_id, guide) for guide in guides])
    # 异步执行
    # result = job.apply_async()
    # 同步执行
    # result = task_group().get()
    return {"company_id": company_id, "results": results}


if __name__ == '__main__':
    recommend_task("91440101717852200L")
