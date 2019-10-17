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
from restful_server.policy import policy_service
from service.base_func import need_to_update_guides
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
        # 记录有效时间，默认为24小时
        expired = request.args.get("recommend_expired_time",
                                   None)
        recommend_records = [one for one in mongo.db.recommend_record.find(
            {"company_id": company_id, "guide_id": {"$in": valid_guides}, "latest": True})]
        guide_ids = need_to_update_guides(company_id, expired, recommend_records)
        for guide_id in guide_ids:
            recommend_task.delay(company_id, guide_id)
        records = []
        for one in recommend_records:
            if is_above_threshold(one, threshold) and not one.get("mismatch_industry",None):
                records.append(one)
        records = sorted(records, key=lambda e:e["score"], reverse=True)
        response_dict["result"] = records
        return jsonify(response_dict)

@policy_service.route("check_recommend/", methods=["GET"])
def check_recommend():
  response_dict = dict()
  company_id = request.args.get("company_id")
  valid_guides = [one["guide_id"] for one in Guide.list_valid_guides()]
  recommend_records = [one for one in mongo.db.recommend_record.find(
     {"company_id": company_id, "guide_id": {"$in": valid_guides}, "latest": True})]
  records = []
  for one in recommend_records:
    if not one.get("mismatch_industry",None):
      records.append(one)
  records = sorted(records, key=lambda e:e["score"], reverse=True)
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
