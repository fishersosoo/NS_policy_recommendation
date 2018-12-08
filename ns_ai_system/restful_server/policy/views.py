# coding=utf-8
import os

from flask import request
from flask_restful import Api, Resource, reqparse

from restful_server.policy import policy_service
from service.file_processing import get_text_from_doc_bytes
from service.policy_graph_construct import build_policy_graph

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


@policy_service.route("understand_file/<string:policy_id>/", methods=["POST"])
def UnderstandPolicyFile(policy_id):
    file_bytes = request.files['file'].read()
    policy_name = os.path.splitext(request.files['file'].filename)[0]
    file_text = get_text_from_doc_bytes(file_bytes)
    # file_text=file_bytes.decode(encoding="utf-8")
    build_policy_graph(file_text, policy_id, policy_name)
    return "", 200


policy_api.add_resource(PolicyUnderstandAPI, "understand/")
policy_api.add_resource(PolicyRecommendAPI, "recommend/")
