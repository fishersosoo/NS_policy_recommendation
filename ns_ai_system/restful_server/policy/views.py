# coding=utf-8
import os
import json
import tempfile

import gridfs
from flask import request, jsonify, abort
from flask_restful import Api, Resource, reqparse

from celery_task import celery_app
from celery_task.policy.base import get_pending_task
from celery_task.policy.tasks import understand_guide_task, recommend_task, create_chain_for_check_recommend, \
    is_above_threshold
from condition_identification.api.text_parsing import paragraph_extract
from data_management.models.guide import Guide
from data_management.models.policy import Policy
from restful_server.policy import policy_service
from restful_server.policy.base import check_callback
from restful_server.server import mongo
from service.file_processing import get_text_from_doc_bytes
from service.rabbit_mq import file_event

policy_api = Api(policy_service)


@policy_service.route("upload_policy/", methods=["POST"])
def upload_policy():
    """
    上传政策文件
    :return:
    """
    policy_file = request.files['file']
    policy_id = request.args.get("policy_id")
    # save file
    mongo.save_file(filename=policy_file.filename,
                    fileobj=policy_file, base="policy_file")
    Policy.create(policy_id=policy_id, file_name=policy_file.filename)
    return jsonify({
        "status": "success"
    })


@policy_service.route("re_understand/", methods=["POST"])
def re_understand():
    guide_id = request.form.get("guide_id")
    _, _, guide_node = Guide.find_by_guide_id(guide_id)
    print(guide_node)
    text = get_text_from_doc_bytes(Guide.get_file(guide_node["file_name"]).read())
    info = paragraph_extract(text)
    task = understand_guide_task.delay(guide_id, text)
    return jsonify({
        "task_id": task.id,
        "status": "SUCCESS"
    })


@policy_service.route("upload_guide/", methods=["POST"])
def upload_guide():
    """
    上传政策指南
    :return:
    """
    guide_file = request.files['file']
    if os.path.splitext(guide_file.filename)[1] not in [".doc", ".txt"]:
        return jsonify({"status": "ERROR", "message": "请上传doc文件"})
    guide_id = request.form.get("guide_id")
    effective = request.form.get("effective", True)
    if guide_id is None:
        return jsonify({"status": "ERROR", "message": "请填充指南id字段：guide_id"})
    doc_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".doc")
    guide_file.save(doc_temp_file)
    doc_temp_file.close()
    info = None
    try:
        text = get_text_from_doc_bytes(doc_temp_file, remove_file=False)
        info = paragraph_extract(text)
        if info is None:
            raise Exception("指南内容格式不正确，无法进行理解")
    except Exception as e:
        os.remove(doc_temp_file.name)
        return jsonify({"status": "ERROR", "message": e})
    with open(doc_temp_file.name, "rb") as f:
        Guide.create(guide_id, guide_file.filename, f, effective=effective)
    file_event(message=json.dumps({"guide_id": guide_id, "event": "add"}), routing_key="event.file.add")
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


@policy_service.route("recommend/", methods=["GET"])
def recommend():
    """
    获取推荐结果
    :return:
    """
    response_dict = dict()
    if "company_id" in request.args:
        valid_guides = [one["guide_id"] for one in Guide.list_valid_guides()]
        # 根据企业id获取推荐，返回结果并异步更新结果
        company_id = request.args.get("company_id")
        threshold = float(request.args.get("threshold", 0.))
        task_result = recommend_task.delay(company_id)
        response_dict["task_id"] = task_result.id
        records = []
        for one in mongo.db.recommend_record.find(
                {"company_id": company_id, "guide_id": {"$in": valid_guides}, "latest": True}):
            if is_above_threshold(one, threshold):
                records.append(one)
        response_dict["result"] = records
        return jsonify(response_dict)
    if "task_id" in request.args:
        # 查看异步任务结果
        task_id = request.args.get("task_id")
        result = recommend_task.AsyncResult(task_id)
        state = result.state
        response_dict['status'] = state
        if state == "SUCCESS":
            results = result.get()
            records = [one for one in
                       mongo.db.recommend_record.find({"company_id": results["company_id"], "latest": True})]
            response_dict["result"] = records
        else:
            response_dict["result"] = []
    return jsonify(response_dict)


@policy_service.route("check_recommend/", methods=["POST"])
def check_single_guide_for_companies():
    """
    多个企业和单个政策的匹配情况
    :return:
    """
    MAX_PENDING = celery_app.conf.get("CELERYD_CONCURRENCY") - 2
    # print(request.headers)
    params = request.json
    if params is None:
        abort(400)
    companies = params.get("companies", [])
    if len(companies) == 0:
        return jsonify({
            "message":
                {
                    "status": "empty companies ",
                    "traceback": "companies字段不能为空"
                }})
    # 检查参数是否正确
    guide_id = params.get("guide_id", None)
    threshold = float(params.get("threshold", .0))
    guide_ = mongo.db.guide_file.find_one({"guide_id": guide_id})
    if guide_ is None:
        return jsonify({
            "task_id": "",
            "message":
                {
                    "status": "NOT_FOUND",
                    "traceback": guide_id
                }})
    callback_ok, callback_stack = check_callback(params.get("callback", None), params.get("guide_id", ))
    if not callback_ok:
        return jsonify({
            "task_id": "",
            "message":
                {
                    "status": "CALLBACK_FAIL",
                    "traceback": callback_stack
                }
        })
    max_input = 20
    if max_input == 0:
        # 队列已满
        return jsonify({
            "task_id": "",
            "message":
                {
                    "status": "FULL",
                    "traceback": companies
                }
        })
    elif max_input >= len(companies):
        # 队列能放进去
        task_id = create_chain_for_check_recommend(companies, threshold, guide_id,
                                                   params.get("callback", None))
        return jsonify({
            "task_id": task_id,
            "message":
                {
                    "status": "SUCCESS",
                    "traceback": None
                }
        })
    else:
        # 队列有空位
        task_id = create_chain_for_check_recommend(companies[:max_input], threshold, guide_id,
                                                   params.get("callback", None))
        return jsonify({
            "task_id": task_id,
            "message":
                {
                    "status": "FULL",
                    "traceback": companies[max_input:]
                }
        })


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
        response = mongo.send_file(guide_["file_name"], base="guide_file")
        response.headers["Content-Disposition"] = "attachment; filename={}".format(guide_["file_name"])
        response.headers["x-suggested-filename"] = guide_["file_name"]
        return response
    else:
        return jsonify({"message": "not found", "guide_id": guide_id})
