# coding=utf-8
import copy
import os
import json
import tempfile
import time

from flask import request, jsonify, abort
from flask_restful import Api

from celery import group
from celery.result import GroupResult
from celery_task.policy.tasks import understand_guide_task, recommend_task, is_above_threshold, update_recommend_record_with_label
from condition_identification.api.text_parsing import Document
from data_management.api.rpc_proxy import rpc_server
from data_management.models.guide import Guide
from data_management.config import redis_cache, py_client
from data_management.models.label import Label
from restful_server.error_handlers import MissingParam
from restful_server.policy import policy_service
from service.base_func import get_needed_check_guides, format_record
from restful_server.server import mongo, app
from service.file_processing import get_text_from_doc_bytes

policy_api = Api(policy_service)


@policy_service.route("re_understand/", methods=["POST"])
def re_understand():
    guide_id = request.form.get("guide_id", None)
    if guide_id is None:
        guides = list(mongo.db.guide_file.find({}))
    else:
        guides = list(mongo.db.guide_file.find({"guide_id": str(guide_id)}))
    for guide in guides:
        if Guide.file_info(guide["file_id"])["contentType"] == "application/msword":
            text = get_text_from_doc_bytes(Guide.get_file(guide["guide_id"]).read())
            task = understand_guide_task.delay(guide["guide_id"], text)
    return jsonify([one["guide_id"] for one in guides])


@policy_service.route("upload_guide/", methods=["POST"])
def upload_guide():
    """
    上传政策指南
    :return:
    """
    guide_file = request.files['file']
    guide_id = request.form.get("guide_id")
    effective = request.form.get("effective", True)
    if guide_id is None:
        return jsonify({"status": "ERROR", "message": "请填充指南id字段：guide_id"})
    doc_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".doc")
    guide_file.save(doc_temp_file)
    doc_temp_file.close()
    if os.path.splitext(guide_file.filename)[1] not in [".doc", ".txt"]:
        with open(doc_temp_file.name, "rb") as f:
            Guide.create(guide_id, guide_file.filename, f, effective=effective)
            os.remove(doc_temp_file.name)
        return jsonify({"status": "ERROR", "message": "非doc或txt文件，文件已保存，但是不会提交理解"})

    info = None
    try:
        text = get_text_from_doc_bytes(doc_temp_file, remove_file=False)
        document = Document.paragraph_extract(text)
        if document is None:
            raise Exception("指南内容格式不正确，无法进行理解")
    except Exception as e:
        os.remove(doc_temp_file.name)
        return jsonify({"status": "ERROR", "message": e})
    with open(doc_temp_file.name, "rb") as f:
        Guide.create(guide_id, guide_file.filename, f, effective=effective)
    rpc_server().rabbitmq.push_message("event.file", "event.file.add", {"guide_id": guide_id, "event": "add"})
    task = understand_guide_task.delay(guide_id, text)
    os.remove(doc_temp_file.name)
    return jsonify({
        "task_id": task.id,
        "status": "SUCCESS"
    })


@policy_service.route("set_guide/", methods=["POST"])
def set_guide():
    """
    修改指南属性

    Returns:

    """
    params = request.json
    guide_id = params.get("guide_id")
    effective = params.get("effective")
    result = mongo.db.guide_file.update_one({"guide_id": guide_id}, {"$set": {"effective": effective}}, upsert=False)
    if effective:
        rpc_server().rabbitmq.push_message("event.file", "event.file.enable", {"guide_id": guide_id, "event": "enable"})
    else:
        rpc_server().rabbitmq.push_message("event.file", "event.file.disable", {"guide_id": guide_id, "event": "disable"})
    return jsonify(result.raw_result)


@policy_service.route("get_result/", methods=["GET"])
def get_result():
    """
    获取理解结果
    :return:
    """
    guide_id = request.args.get("guide_id", None)
    if guide_id is None:
        return jsonify(list(mongo.db.parsing_result.find({})))
    else:
        return jsonify(list(mongo.db.parsing_result.find({"guide_id": str(guide_id)})))


@policy_service.route("recommend/", methods=["POST"])
def recommend():
    """
    获取推荐结果
    :return:
    """
    response_dict = dict()
    params = request.json
    company_id = params.get("company_id", None)
    if company_id is None:
        raise MissingParam("company_id")
    labels = params.get("label", [])
    labels = Label.convert_texts(labels)
    threshold = float(params.get("threshold", 0.))
    expired = params.get("recommend_expired_time", None)  # 记录有效时间，默认为24小时
    valid_guides = [one["guide_id"] for one in Guide.list_valid_guides()]  # 有效政策
    # 根据企业id获取推荐，返回结果并异步更新结果
    recommend_records_no_label = [one for one in mongo.db.recommend_record.find(
        {"company_id": company_id, "has_label": False, "guide_id": {"$in": valid_guides}, "latest": True},{"_id":0})]
    # TODO: 如mongoDB压力较大这里的in操作改在代码中实现
    guide_ids = get_needed_check_guides(company_id, expired, recommend_records_no_label)
    task_id = create_task_if_not_executing(company_id, guide_ids)
    # 如果task_id有的话
    if task_id:
        # 等待缓存的task状态变为已完成
        while redis_cache.get(task_id) is not None and int(redis_cache.get(task_id)) != 1:
            time.sleep(1)
        recommend_records_no_label = [one for one in mongo.db.recommend_record.find(
        {"company_id": company_id, "has_label": False, "guide_id": {"$in": valid_guides}, "latest": True},{"_id":0})]
    records = []  # 保存记录返回结果
    total_labels_match_count = copy.deepcopy(labels)  # 保存label使用情况
    for label in total_labels_match_count:
        label["match_count"] = 0
    guide_ids_with_label = [] # 记录要插入recommend_record_with_label表中的政策id
    record_to_update = [] # 记录带有标签的匹配结果
    for one_result_without_label in recommend_records_no_label:
        if not one_result_without_label.get("mismatch_industry", None):
            one_result_with_label, labels_with_match_count = match_with_labels(one_result_without_label, labels)
            labels_match_count_for_validation = label_validation(company_id, one_result_without_label["guide_id"],
                                                                 labels, labels_with_match_count)
            update_labels_match_count(total_labels_match_count, labels_match_count_for_validation)
            # 将one_result_with_label覆盖带标签的历史纪录（插入数据库）
            guide_ids_with_label.append(one_result_without_label["guide_id"])
            record_to_update.append(copy.deepcopy(one_result_with_label))
            # py_client.ai_system["recommend_record_with_label"].delete_many({"company_id": company_id,
            #                                              "guide_id": one_result_without_label["guide_id"]})
            # py_client.ai_system["recommend_record_with_label"].insert_one(copy.deepcopy(one_result_with_label))
            formatted_record = format_record(one_result_with_label)
            if is_above_threshold(formatted_record, threshold):
                records.append(formatted_record)
    if record_to_update:
        # 转换成字符串格式，才能作为消息传到队列中
        for one in record_to_update:
            del one["time"]
        update_recommend_record_with_label.delay(company_id, json.dumps(guide_ids_with_label), json.dumps(record_to_update))
        # py_client.ai_system["recommend_record_with_label"].delete_many({"company_id": company_id,
        #                                     "guide_id": {"$in": guide_ids_with_label}})
        # py_client.ai_system["recommend_record_with_label"].insert_many(record_to_update)
    # 检查每个label的match_count将有用标签添加到标签库(使用Label类函数)
    expired_match_count = py_client.ai_system["config"].find_one({"expired_match_count": {'$exists': True}})[
            "expired_match_count"]
    expired_match_count = float(expired_match_count)
    for label in total_labels_match_count:
        if label["match_count"] > expired_match_count:
            Label.add_label(label["text"])
    # 返回的记录按score倒序
    if records:
        records = sorted(records, key=lambda e: e["score"], reverse=True)
    response_dict["result"] = records
    return jsonify(response_dict)


def update_labels_match_count(total_labels_match_count, labels_match_count):
    """
    更新保存label使用情况
    Args:
        total_labels_match_count:
        labels_match_count:

    Returns:

    """
    for total_label, one_label in zip(total_labels_match_count, labels_match_count):
        total_label["match_count"] += one_label.get("match_count", 0)
    return total_labels_match_count


def label_validation(company_id, guide_id, labels, default_labels_with_match_count=None):
    """
    检查标签是否有效.
    查找带标签的历史记录，然后用标签列表检查没匹配的条件，计算出每个标签的匹配数量
    Args:
        company_id: 企业id
        guide_id: 政策id
        labels: 标签序列
        default_labels_with_match_count:

    Returns:

    """
    if default_labels_with_match_count is None:
        default_labels_with_match_count = dict()
    old_result_with_label = py_client.ai_system["recommend_record_with_label"].find_one(
        {"company_id":company_id, "guide_id":guide_id})  # 从数据库取出带标签的历史记录
    if old_result_with_label is None:
        return default_labels_with_match_count
    _, labels_with_match_count = match_with_labels(old_result_with_label, labels)
    return labels_with_match_count

def is_match_label(value, label):
    """

    Args:
        label: {"_id":"","text":""}
        value: "政策文本"

    Returns:
        bool. 标签和文本是否匹配
    """
    if type(value) == list:
        for v in value:
            if label["text"] in v:
                return True
        return False
    else:
        return label["text"] in value


def match_with_labels(recommend_record_no_label, labels):
    """
    使用标签对异步计算的结果进行调整
    Args:
        recommend_record_no_label: 单个异步计算结果
        labels: 标签列表.[{"_id":"","text":""}]

    Returns:
       recommend_record_with_label.和recommend_record_no_label结果相似，多了label字段

        {
        "company_id": "",
        "label":["",],
        "guide_id": "",
        "time": datetime.datetime.utcnow(),
        "latest": True,
        "has_label": False,
        "sentences": [
            {
                "text":"",
                "type": "正常",
                "result": "",
                "clauses":[
                    {
                        "fields":["专利名称",],
                        "relation":"是",
                        "value":"规定航运物流",
                        "result":"mismatch"
                    },
                ]
            }
        ]
    }

       labels.每个label增加了match_count表示匹配了多少个条件
       [
       {"_id":"",
       "text":"",
       "match_count":0,},
       ]
    """
    labels_with_match_count = copy.deepcopy(labels)
    recommend_record_with_label = copy.deepcopy(recommend_record_no_label)
    recommend_record_with_label["has_label"] = True
    recommend_record_with_label["label"] = []
    for sentence in recommend_record_with_label["sentences"]:
        if sentence["type"] != "正常" and len(sentence["clauses"]) != 0:
            continue
        for clause in sentence["clauses"]:
            if clause["result"] != "match" and clause.get("value", None) is not None:
                for label in labels_with_match_count:
                    is_match = is_match_label(clause["value"], label)
                    if is_match:
                        clause["result"] = "match"
                        sentence["result"] = "match"
                        if "match_count" not in label:
                            label["match_count"] = 1
                        else:
                            label["match_count"] += 1
    for label in labels_with_match_count:
        if label.get("match_count", 0) != 0:
            recommend_record_with_label["label"].append(label["text"])
    return recommend_record_with_label, labels_with_match_count


def create_task_if_not_executing(company_id, guide_ids):
    """
    用redis缓存当前正在执行任务的企业，如果发现该企业正在执行任务，就不再插入队列中
    Args:
        company_id:
        guide_ids:

    Returns:

    """
    if not guide_ids:
        return None
    # 先从缓存中查看是否正在进行计算
    executing_task_id = redis_cache.get(f"executing-{company_id}")
    # 如果没有
    if executing_task_id is None:
        recommend_tasks = [recommend_task.s(company_id, guide_id) for guide_id in guide_ids]
        promise = group(recommend_tasks)()
        # 将company_id作为键，task_id作为值存起来
        redis_cache.set(f"executing-{company_id}", promise.id, ex=900)
        # 缓存task的状态
        redis_cache.set(promise.id, 0, ex=900)
        # 阻塞等待结果返回
        promise.get()
        # 结果返回后修改缓存的状态
        redis_cache.set(promise.id, 1, ex=900)
        executing_task_id = promise.id
    # 返回任务id
    return executing_task_id
    # executing_ids = redis_cache.get("executing_ids")
    # if executing_ids is None:
    #     redis_cache.set('executing_ids', company_id, ex=90)
    #     recommend_tasks = [recommend_task.s(company_id, guide_id) for guide_id in guide_ids]
    #     return group(recommend_tasks)
    #     # for guide_id in guide_ids:
    #     #     recommend_task.delay(company_id, guide_id)
    # else:
    #     executing_ids_list = executing_ids.split(",")
    #     if company_id not in executing_ids_list:
    #         executing_ids = f"{executing_ids},{company_id}"
    #         redis_cache.set('executing_ids', executing_ids, ex=90)
    #         recommend_tasks = [recommend_task.s(company_id, guide_id) for guide_id in guide_ids]
    #         return group(recommend_tasks)
    #         # for guide_id in guide_ids:
    #         #     recommend_task.delay(company_id, guide_id)


@policy_service.route("check_recommend/", methods=["GET"])
def check_recommend():
    response_dict = dict()
    company_id = request.args.get("company_id")
    valid_guides = [one["guide_id"] for one in Guide.list_valid_guides()]
    recommend_records = [one for one in mongo.db.recommend_record.find(
        {"company_id": company_id, "guide_id": {"$in": valid_guides}, "latest": True})]
    records = []
    for one in recommend_records:
        if not one.get("mismatch_industry", None):
            records.append(one)
    records = sorted(records, key=lambda e: e["score"], reverse=True)
    response_dict["result"] = records
    return jsonify(response_dict)


@policy_service.route("single_recommend/", methods=["GET"])
def single_recommend():
    company_id = request.args.get("company_id", None)
    guide_id = request.args.get("guide_id", None)
    return jsonify(mongo.db.recommend_record.find_one({"guide_id": guide_id, "company_id": company_id, "latest": True}))


@policy_service.route("guide_file/", methods=["GET"])
def download_guide_file():
    guide_id = request.args.get("guide_id")
    guide_ = mongo.db.guide_file.find_one({"guide_id": guide_id})
    if guide_ is not None:
        grid_out = Guide.get_file(guide_id)
        if grid_out is None:
            return jsonify({"message": "not found", "guide_id": guide_id})
        response = app.response_class(
            grid_out.read(),
            mimetype=grid_out.content_type,
            direct_passthrough=True,
        )
        response.content_length = grid_out.length
        response.last_modified = grid_out.upload_date
        response.set_etag(grid_out.md5)
        response.cache_control.public = True
        response.make_conditional(request)
        response.headers["Content-Disposition"] = "attachment; filename={}".format(guide_["file_name"])
        response.headers["x-suggested-filename"] = guide_["file_name"]
        return response
    else:
        return jsonify({"message": "not found", "guide_id": guide_id})


@policy_service.route("guides/", methods=["GET"])
def list_guide():
    """
    返回状态
    """

    ret = []
    for one_guide in Guide.list_guide():
        file_info = Guide.file_info(one_guide["file_id"])
        paring_info = Guide.parsing_info(one_guide["guide_id"])
        if file_info.get("uploadDate") != None and paring_info.get("doneTime") != None:
            if paring_info.get("doneTime") < file_info.get("uploadDate"):
                after = file_info.get("uploadDate") - paring_info.get("doneTime")
                after = f"- {str(after)}"
            else:
                after = paring_info.get("doneTime") - file_info.get("uploadDate")
        else:
            after = "政策未理解"
        ret.append({"guide_id": one_guide["guide_id"],
                    "effective": one_guide.get("effective"),
                    "filename": file_info.get("filename"),
                    "contentType": file_info.get("contentType"),
                    "uploadDate": str(file_info.get("uploadDate")),
                    "doneDate": str(paring_info.get("doneTime")),
                    "processAfterUpload": str(after)
                    })
    return jsonify(ret)