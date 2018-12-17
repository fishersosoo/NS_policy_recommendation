# coding=utf-8

from flask import request, jsonify
from flask_restful import Api, Resource, reqparse

from celery_task.policy.tasks import understand_guide_task, recommend_task
from data_management.models.guide import Guide
from data_management.models.policy import Policy
from restful_server.policy import policy_service
from restful_server.server import mongo

policy_api = Api(policy_service)


class PolicyUnderstandAPI(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument("id", type=str, required=True)
    post_parser.add_argument("content", type=str, required=True)

    def post(self):
        kwargs = self.post_parser.parse_args()
        return {}, 200


class PolicyRecommendAPI(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("id", type=str, required=True)

    def get(self):
        kwargs = self.get_parser.parse_args()
        return {}, 200


@policy_service.route("upload_policy/", methods=["POST"])
def upload_policy():
    policy_file = request.files['file']
    policy_id = request.args.get("policy_id")
    # save file
    mongo.save_file(filename=policy_file.filename,
                    fileobj=policy_file, base="policy_file")
    Policy.create(policy_id=policy_id, file_name=policy_file.filename)
    return jsonify({
        "status": "success"
    })


@policy_service.route("upload_guide/", methods=["POST"])
def upload_guide():
    guide_file = request.files['file']
    guide_id = request.args.get("guide_id")
    mongo.save_file(filename=guide_file.filename,
                    fileobj=guide_file, base="guide_file")
    Guide.create(guide_id=guide_id, file_name=guide_file.filename)
    policy_id = request.args.get("policy_id", default=None)
    if policy_id is not None:
        Guide.link_to_policy(guide_id, policy_id)
    result = understand_guide_task.delay(guide_id)
    return jsonify({
        "task_id": result.id,
        "status": "SUCCESS"
    })


@policy_service.route("recommend/", methods=["GET"])
def recommend():
    response_dict = dict()
    if "company_id" in request.args:
        company_id = request.args.get("company_id")
        task_result = recommend_task.delay(company_id)
        response_dict["task_id"] = task_result.id
        records = [one for one in mongo.db.recommend_record.find({"company_id": company_id, "latest": True})]
        response_dict["result"] = records
        return jsonify(response_dict)
    if "task_id" in request.args:
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


policy_api.add_resource(PolicyUnderstandAPI, "understand/")
policy_api.add_resource(PolicyRecommendAPI, "recommend/")
