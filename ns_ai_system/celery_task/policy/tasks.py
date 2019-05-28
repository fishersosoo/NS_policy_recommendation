# coding=utf-8
import datetime
import traceback
import copy
import requests
from celery import group, chain, chord
from celery.result import allow_join_result
from flask_jsonrpc.proxy import ServiceProxy

from celery_task import celery_app, log, config
from data_management.config import dataService, py_client
from data_management.models import UUID
from data_management.models.guide import Guide
from data_management.models.word import Word
from service import conert_ch2num
import numpy as np
from service.policy_graph_construct import understand_guide
from celery import group


# @celery_app.task(rate_limit="2/h")
@celery_app.task
def understand_guide_task(guide_id, text):
    """

    :param guide_id: 指南的外部id
    :return:
    """
    understand_guide(guide_id, text)


@celery_app.task
def check_single_guide(company_id, guide_id, threshold=.0):
    """
    检查单个指南和企业的匹配信息，如果存在匹配则存放到数据库中
    :param company_id:企业id
    :param guide_id:指南的平台id
    :return:
    """
    try:
        matched_sentence_id = set()
        ret = py_client.ai_system["parsing_result"].find_one({"guide_id": str(guide_id)})
        assert ret is not None
        sentences = ret.get("sentences", None)
        triples = ret["triples"]
        reasons = []
        fail_to_check = 0
        checked_fields = []
        for triple in triples:
            if len(triple["fields"]) == 0:
                continue
            if triple["fields"][0] in checked_fields:
                continue
            match, reason = check_single_requirement(company_id, triple)
            if match is None:
                fail_to_check += 1
            else:
                checked_fields.append(triple["fields"][0])
            if match:
                reasons.append(f'{len(reasons)+1}. {triple["sentence"]}【{reason}】\n')
                if "sentence_id" in triple:
                    matched_sentence_id.add(triple["sentence_id"])
        if sentences is not None:
            ids=list(sentences.keys())
            for id in ids:
                if sentences[id] == "":
                    sentences.pop(id)
            mismatched_sentence_id = set(sentences.keys()) - matched_sentence_id
            log.info(mismatched_sentence_id)
        else:
            mismatched_sentence_id = None
        record = format_record(company_id, len(triples) - fail_to_check, guide_id, reasons, sentences,
                               mismatched_sentence_id)
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
                  time=datetime.datetime.now(),
                  latest=True
                  )
    return record


def check_single_requirement(company_id, triple):
    """
    检查企业是否满足单一条件
    :param company_id: 企业id
    :return: match, reason. match表示是否满足，reason，如果不满足则原因为None
    """
    if "独立法人资格" in triple["value"]:
        return True, "是"
    if len(triple["fields"]) == 0:
        return None, None
    field = triple["fields"][0]
    field_info = py_client.ai_system["field"].find_one({"item_name": field})
    if field_info is None:
        log.info(f"no field {field}")
        return None, None
    # query_data
    ip = config.get('data_server', 'host')
    url = f"http://{ip}:3306/data"
    server = ServiceProxy(service_url=url)
    return_data = server.data.sendRequest(company_id, f"{field_info['resource_id']}.{field_info['item_id']}")
    data = return_data.get("result", None)
    if data is None:
        log.info(f"{return_data}")
        return None, None
    if triple["relation"] in ["大于", "小于"]:
        return compare_literal(data, triple)
    else:
        if triple["relation"] == "位于":
            if triple["value"] in data[0]:
                return True, data[0]
            else:
                return False, data[0]
        if triple["relation"] == "否":
            if triple["value"] not in data[0]:
                return True, data[0]
            else:
                return False, data[0]
        if triple["relation"] == "是":
            if triple["value"] in data[0]:
                return True, data[0]
            else:
                return False, data[0]


def compare_literal(data, triple):
    query_values = []
    for one_data in data:
        try:
            query_values.append(float(one_data))
        except:
            pass
    if len(query_values) == 0:
        log.info(f"can not convert value of {triple['fields'][0]} to float")
        return None, None
    try:
        value = conert_ch2num(triple["value"])
    except:
        log.info(f"can not convert value \"{triple['value']}\" to float")
        return None, None
    if triple["relation"] == "大于":
        for query_value in query_values:
            if query_value > value:
                return True, query_value
        return False, query_values[0]
    else:
        for query_value in query_values:
            if query_value < value:
                return True, query_value
        return False, query_values[0]


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
    if qualify_certify_count == 0:
        base_info["FQZ_ZZMC"] = []
    else:
        qualifies = \
            dataService.sendRequest("getQualifyCertifyInfo",
                                    {"entName": company_name, 'pageNo': 1, "pageSize": qualify_certify_count})[
                "RESULTDATA"]
        base_info["FQZ_ZZMC"] = [one["FQZ_ZZMC"] for one in qualifies]
    return base_info


@celery_app.task
def recommend_task(company_id, threshold=.0):
    """
    更新指定企业的推荐记录
    :param company_id: 企业id
    :param threshold: 匹配度阈值（尚未使用），只有企业与指南匹配度高于此值时候才会推荐
    :return:
    """
    log.info(f"recommend_task for company: {company_id}")
    guides = list(py_client.ai_system["parsing_result"].find({}))
    results = []
    for guide in guides:
        result = check_single_guide(company_id, guide["guide_id"])
        if result is not None:
            results.append(result)
    # task_group = group([check_single_guide.s(company_id, guide) for guide in guides])
    # 异步执行
    # result = job.apply_async()
    # 同步执行
    # result = task_group().get()
    return {"company_id": company_id, "results": results}


def is_above_threshold(result, threshold):
    try:
        return float(result["matching"]) >= float(threshold)
    except:
        return False


@celery_app.task(bind=True,default_retry_delay=300, max_retries=0)
def check_single_guide_batch_companies(self,companies, threshold, guide_id,url):
    """
    创建多个子任务检查企业是否满足，阻塞获取所有任务结果

    :param companies:
    :param threshold:
    :param guide_id:
    :return:
    """
    results = []
    for company in companies:
        results.append(check_single_guide.delay(company, guide_id))
    group_result = []
    with allow_join_result():
        for result in results:
            group_result.append(result.get())
    return_result = {company: {"matching": .0, "status": "FAIL"} for company in companies}
    for result in group_result:
        if is_above_threshold(result, threshold):
            return_result[result["company_id"]] = {"matching": result["matching"], "status": "SUCCESS"}
    push_single_guide_result.delay(guide_id=guide_id, url=url, task_id=self.request.id)
    return return_result


@celery_app.task(default_retry_delay=1000, max_retries=1)
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
    task_result = check_single_guide_batch_companies.delay(companies=companies, threshold=threshold, guide_id=guide_id,url=url)
    return task_result.id
