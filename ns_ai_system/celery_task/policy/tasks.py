# coding=utf-8
import copy
import datetime
import traceback
from enum import Enum, unique


from celery_task import celery_app, log, config,rpc_server
from data_management.config import py_client
from service import conert_ch2num
from service.policy_graph_construct import understand_guide


@unique
class MatchResult(Enum):
    """
    表示匹配结果
    """
    MISMATCH = 0
    MATCH = 1
    UNRECOGNIZED = 2


@celery_app.task
def status_check():
    """
    检查状态

    Returns:

    """
    pass


# @celery_app.task(rate_limit="2/h")
@celery_app.task
def understand_guide_task(guide_id, text):
    """

    :param guide_id: 指南的外部id
    :return:
    """
    understand_guide(guide_id, text)


@celery_app.task
def check_single_guide(company_id, guide_id, routing_key, threshold=.0):
    """

    Args:
        company_id:
        guide_id:
        routing_key:
        threshold:

    Returns:

    """
    record = _check_single_guide(company_id, guide_id, threshold=threshold)
    if record is None:
        rpc_server.rabbitmq.push_message("task", routing_key, {"company_id": company_id, "guide_id": guide_id, "score": None})
    else:
        rpc_server.rabbitmq.push_message("task", routing_key, {"company_id": company_id, "guide_id": guide_id, "score": record["score"]})
    return record


def _check_single_guide(company_id, guide_id, threshold=.0):
    """
    检查单个指南和企业的匹配信息，如果存在匹配则存放到数据库中
    :param company_id:企业id
    :param guide_id:指南的平台id
    :return:
    """
    record = {"mismatch": [], "match": [], "unrecognized": []}
    cached_data = dict()
    mismatched_sentence_id = set()
    matched_sentence_id = set()
    ret = py_client.ai_system["parsing_result"].find_one({"guide_id": str(guide_id)})
    if ret is None:
        log.info(f"guide_id:{guide_id} not found or have not been processed.")
        return None
    sentences = ret.get("sentences", None)
    triples = ret["triples"]
    for triple in triples:
        if len(triple["fields"]) == 0:
            continue
        match, data, cached_data = check_single_requirement(company_id, triple, cached_data)
        if match == MatchResult.MISMATCH:
            if triple["sentence_id"] not in matched_sentence_id:
                mismatched_sentence_id.add(triple["sentence_id"])
        if match == MatchResult.MATCH:
            if triple["sentence_id"] not in matched_sentence_id:
                record["match"].append(
                    {"sentence": triple["sentence"]})
            # record["match"].append(
            #     {"sentence": triple["sentence"], "data": {"field": triple["fields"][0], "value": data}})
            matched_sentence_id.add(triple["sentence_id"])
            if triple["sentence_id"] in mismatched_sentence_id:
                mismatched_sentence_id.remove(triple["sentence_id"])
    unrecognized_sentence_id = set(sentences.keys()) - matched_sentence_id - mismatched_sentence_id
    for one in unrecognized_sentence_id:
        record["unrecognized"].append(sentences[one])
    for one in mismatched_sentence_id:
        record["mismatch"].append(sentences[one])
    record["company_id"] = company_id
    record["guide_id"] = guide_id
    record["time"] = datetime.datetime.utcnow()
    if (len(record["mismatch"]) + len(record["match"])) == 0:
        record["score"] = 0
    else:
        record["score"] = len(record["match"]) / (len(record["mismatch"]) + len(record["match"]))
    record["latest"] = True
    py_client.ai_system["recommend_record"].delete_many({"company_id": company_id,
                                                         "guide_id": guide_id})
    py_client.ai_system["recommend_record"].insert_one(copy.deepcopy(record))
    return record


def check_single_requirement(company_id, triple, cached_data):
    """
    检查企业是否满足单一条件

    Args:
        cached_data: 缓存的数据
        company_id: 企业id
        triple: 三元组

    Returns:
        MatchResult, Data, cached_data
        MatchResult类表示是否满足或者未识别.
        Data，表示企业真实数据
    """

    if "独立法人资格" in triple["value"]:
        return MatchResult.MATCH, "", cached_data
    field = triple["fields"][0]
    field_info = py_client.ai_system["field"].find_one({"item_name": field})
    if field_info is None:
        log.info(f"no field {field}")
        return MatchResult.UNRECOGNIZED, "", cached_data
    data = cached_data.get(f"{field_info['resource_id']}.{field_info['item_id']}", None)
    if data is None:
        # query_data
        start_t = datetime.datetime.utcnow()
        return_data = rpc_server.data.sendRequest(company_id, f"{field_info['resource_id']}.{field_info['item_id']}")
        data = return_data.get("result", None)
    if data is None:
        log.info(f"{return_data}")
        return MatchResult.UNRECOGNIZED, "", cached_data
    else:
        cached_data[f"{field_info['resource_id']}.{field_info['item_id']}"] = data
    if triple["relation"] in ["大于", "小于"]:
        match, data = compare_literal(data, triple)
        return match, data, cached_data
    else:
        if triple["relation"] == "位于":
            if triple["value"] in data[0]:
                return MatchResult.MATCH, data[0], cached_data
            else:
                return MatchResult.MISMATCH, data[0], cached_data
        if triple["relation"] == "否":
            if triple["value"] not in data[0]:
                return MatchResult.MATCH, data[0], cached_data
            else:
                return MatchResult.MISMATCH, data[0], cached_data
        if triple["relation"] == "是":
            if triple["value"] in data[0]:
                return MatchResult.MATCH, data[0], cached_data
            else:
                return MatchResult.MISMATCH, data[0], cached_data


def compare_literal(data, triple):
    query_values = []
    for one_data in data:
        try:
            query_values.append(float(one_data))
        except:
            pass
    if len(query_values) == 0:
        log.info(f"can not convert value of {triple['fields'][0]} to float")
        return MatchResult.UNRECOGNIZED, ""
    try:
        value = conert_ch2num(triple["value"])
    except:
        log.info(f"can not convert value \"{triple['value']}\" to float")
        return MatchResult.UNRECOGNIZED, ""
    if triple["relation"] == "大于":
        for query_value in query_values:
            if query_value > value:
                return MatchResult.MATCH, query_value
        return MatchResult.MISMATCH, query_values[0]
    else:
        for query_value in query_values:
            if query_value < value:
                return MatchResult.MATCH, query_value
        return MatchResult.MISMATCH, query_values[0]


@celery_app.task
def recommend_task(company_id, guide_id, threshold=.0):
    """
    更新指定企业的推荐记录
    :param company_id: 企业id
    :param threshold: 匹配度阈值（尚未使用），只有企业与指南匹配度高于此值时候才会推荐
    :param guide_id: 政策id
    :return:
    """
    try:
        log.info(f"recommend_task for company: {company_id}")
        log.info(f"recommend_task for guide: {guide_id}")
        # guides = list(Guide.list_valid_guides())
        # results = []
        # for guide in guides:
        result = _check_single_guide(company_id, guide_id)
        # if result is not None:
        # results.append(result)
        # task_group = group([check_single_guide.s(company_id, guide) for guide in guides])
        # 异步执行
        # result = job.apply_async()
        # 同步执行
        # result = task_group().get()
        return {"company_id": company_id, "result": result}
    except Exception as e:
        log.error(str(guide_id))
        log.error(traceback.format_exc())
        return None


def is_above_threshold(result, threshold):
    try:
        return float(result["score"]) >= float(threshold)
    except:
        return False
