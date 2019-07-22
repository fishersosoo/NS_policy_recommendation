# coding=utf-8
import copy
import datetime
import traceback
from enum import Enum, unique

import requests
from celery.result import allow_join_result
from flask_jsonrpc.proxy import ServiceProxy

from celery_task import celery_app, log, config
from celery_task.policy.base import push_message
from data_management.config import dataService, py_client
from data_management.models.guide import Guide
from data_management.models.word import Word
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
        push_message(routing_key, {"company_id": company_id, "guide_id": guide_id, "score": None})
    else:
        push_message(routing_key, {"company_id": company_id, "guide_id": guide_id, "score": record["score"]})
    return record


def _check_single_guide(company_id, guide_id, threshold=.0):
    """
    检查单个指南和企业的匹配信息，如果存在匹配则存放到数据库中
    :param company_id:企业id
    :param guide_id:指南的平台id
    :return:
    """
    try:
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
    except Exception as e:
        log.error(str(guide_id))
        log.error(traceback.format_exc())
        return None


def format_record(company_id, count, guide_id, reasons, sentences, mismatched_sentence_id):
    count = 1 if count == 0 else count
    matching = len(reasons) / count
    if matching < 0.2 and matching != 0:
        matching += 0.2
    reasons = "\n".join(reasons)
    reasons = f"企业满足以下条件：【括号中内容为企业的真实情况】\n{reasons}"
    if sentences is not None:
        mismatch = "未满足或无法匹配条件：\n"
        for index, sentence_id in enumerate(mismatched_sentence_id):
            mismatch += f"{index+1}. {sentences.get(sentence_id,'')}\n"
        reasons += mismatch
    record = dict(company_id=company_id,
                  guide_id=guide_id,
                  reason=reasons,
                  matching=matching,
                  time=datetime.datetime.utcnow(),
                  latest=True
                  )
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
        ip = config.get('data_server', 'host')
        url = f"http://{ip}:{config.get('data_server','port')}/data"
        server = ServiceProxy(service_url=url)
        return_data = server.data.sendRequest(company_id, f"{field_info['resource_id']}.{field_info['item_id']}")
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


@celery_app.task
def recommend_task(company_id, guide_id, threshold=.0):
    """
    更新指定企业的推荐记录
    :param company_id: 企业id
    :param threshold: 匹配度阈值（尚未使用），只有企业与指南匹配度高于此值时候才会推荐
    :param guide_id: 政策id
    :return:
    """
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


def is_above_threshold(result, threshold):
    try:
        return float(result["score"]) >= float(threshold)
    except:
        return False


@celery_app.task(bind=True, default_retry_delay=300, max_retries=0, soft_time_limit=60)
def check_single_guide_batch_companies(self, companies, threshold, guide_id, url):
    """
    创建多个子任务检查企业是否满足，阻塞获取所有任务结果

    :param companies:
    :param threshold:
    :param guide_id:
    :return:
    """
    results = []
    for company in companies:
        results.append(_check_single_guide.delay(company, guide_id))
    group_result = []
    with allow_join_result():
        for result in results:
            group_result.append(result.get())
    return_result = {company: {"matching": .0, "status": "FAIL"} for company in companies}
    for result in group_result:
        if result is not None and is_above_threshold(result, threshold):
            return_result[result["company_id"]] = {"matching": result["matching"], "status": "SUCCESS"}
    push_single_guide_result.delay(guide_id=guide_id, url=url, task_id=self.request.id)
    return return_result


@celery_app.task
def push_single_guide_result(guide_id, url, task_id):
    """
    将批量检查企业的任务结果推送到指定url

    :param task_result:
    :param guide_id:指南id
    :param url:推送接收地址
    :return:
    """
    task_result = check_single_guide_batch_companies.AsyncResult(task_id)
    with allow_join_result():
        return_result = task_result.get()
    requests.post(url, json={
        "guide_id": guide_id,
        "task_id": task_id,
        "result": return_result
    })


def create_chain_for_check_recommend(companies, threshold, guide_id, url):
    """
    创建任务组检查多个企业，创建推送任务

    :param companies: 企业id列表
    :param threshold: 匹配度过滤阈值
    :param guide_id: 指南id
    :param url: 推送连接
    :return: 任务id
    """
    task_result = check_single_guide_batch_companies.delay(companies=companies, threshold=threshold, guide_id=guide_id,
                                                           url=url)
    return task_result.id
