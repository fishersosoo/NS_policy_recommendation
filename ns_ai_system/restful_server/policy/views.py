# coding=utf-8
import os
import json
import tempfile

from flask import request, jsonify, abort
from flask_restful import Api

from celery_task.policy.tasks import understand_guide_task, recommend_task, is_above_threshold
from condition_identification.api.text_parsing import Document
from data_management.api.rpc_proxy import rpc_server
from data_management.models.guide import Guide
from data_management.config import redis_cache
from data_management.models.label import Label
from restful_server.error_handlers import MissingParam
from restful_server.policy import policy_service
from service.base_func import need_to_update_guides
from restful_server.server import mongo, app
from service.file_processing import get_text_from_doc_bytes

policy_api = Api(policy_service)


# redis_cache.set("test", ['123'], ex=1)

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
        {"company_id": company_id, "guide_id": {"$in": valid_guides}, "latest": True})]
    # TODO: 如mongoDB压力较大这里的in操作改在代码中实现
    guide_ids = need_to_update_guides(company_id, expired, recommend_records_no_label)
    create_task_if_not_executing(company_id, guide_ids)
    records = []
    for one_result_without_label in recommend_records_no_label:
        if not one_result_without_label.get("mismatch_industry", None):
            one_result_with_label = match_with_labels(one_result_without_label, labels)
            if is_above_threshold(one_result_with_label, threshold):
                records.append(one_result_with_label)
    # 无历史带标签记录，用新带标签结果对比无标记记录
    # 有历史带标签记录，用新带标签结果对比历史带标签记录
    # 将新带标签结果入库
    # TODO:
    records = sorted(records, key=lambda e: e["score"], reverse=True)
    response_dict["result"] = records
    return jsonify(response_dict)


def match_with_labels(recommend_record_no_label, labels):
    """
    使用标签对异步计算的结果进行调整
    Args:
        recommend_record_no_label: 单个异步计算结果
        labels: 标签列表

    Returns:
        最终返回的结果
            {
                "_id": "5da989d9cbd02963add9218e",
                "company_id": "91440101668125196C",
                "guide_id": "220",
                "latest": true,
                "label":["匹配的企业标签1","匹配的企业标签2"],
                "match": [
                    {
                        "score": 0.5,
                        "sentence": "部分匹配的条件1"
                    },
                    {
                        "score": 0.5,
                        "sentence": "部分匹配的条件2"
                    }
                ],
                "mismatch": [
                    {
                        "sentence": "不匹配的条件1"
                    },
                    {
                        "sentence": "不匹配的条件2"
                    }
                ],
                "score": 0.5,
                "time": "Fri, 18 Oct 2019 09:46:01 GMT",
                "unrecognized": [
                    {
                        "sentence": "未识别条件1"
                    }]
            }
    """
    return {
        "_id": "5da989d9cbd02963add9218e",
        "company_id": "91440101668125196C",
        "guide_id": "220",
        "latest": True,
        "label": ["匹配的企业标签1", "匹配的企业标签2"],
        "match": [
            {
                "score": 0.5,
                "sentence": "部分匹配的条件1"
            },
            {
                "score": 0.5,
                "sentence": "部分匹配的条件2"
            }
        ],
        "mismatch": [
            {
                "sentence": "不匹配的条件1"
            },
            {
                "sentence": "不匹配的条件2"
            }
        ],
        "score": 0.5,
        "time": "Fri, 18 Oct 2019 09:46:01 GMT",
        "unrecognized": [
            {
                "sentence": "未识别条件1"
            }]
    }


def create_task_if_not_executing(company_id, guide_ids):
    """
    用redis缓存当前正在执行任务的企业，如果发现该企业正在执行任务，就不再插入队列中
    Args:
        company_id:
        guide_ids:

    Returns:

    """
    executing_ids = redis_cache.get("executing_ids")
    if executing_ids is None:
        redis_cache.set('executing_ids', company_id, ex=900)
        for guide_id in guide_ids:
            recommend_task.delay(company_id, guide_id)
    else:
        executing_ids_list = executing_ids.split(",")
        if company_id not in executing_ids_list:
            executing_ids = f"{executing_ids},{company_id}"
            redis_cache.set('executing_ids', executing_ids, ex=900)
            for guide_id in guide_ids:
                recommend_task.delay(company_id, guide_id)


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
