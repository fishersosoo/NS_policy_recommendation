# coding=utf-8
from flask import request, url_for
from flask_restful import Api, Resource, reqparse

from bonus_identify.Tree import DocTree
from graph_access import build_policy_graph
from models.policy import Policy
from predicate_extraction.tuple_bonus_recognize import TupleBonus
from restful_server.policy import policy_service

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


@policy_service.route("/")
def x():
    print(url_for("policy_service.UnderstandPolicyFile"))
    return "", 200


@policy_service.route("understand_file/", methods=["GET","POST"])
def UnderstandPolicyFile():
    file = request.files['file'].read()
    # print(file)
    policy = Policy.create(content=request.files['file'].filename)
    tree = DocTree()
    tree.construct_from_bytes(file)
    dict_dir = r"Y:\Nansha AI Services\condition_identification\res\word_segmentation"
    tuplebonus = TupleBonus(dict_dir, if_edit_hanlpdict=0)
    tuplebonus.bonus_tuple_analysis(tree)
    build_policy_graph(policy, tuplebonus.get_bonus_tree())
    return "", 200


policy_api.add_resource(PolicyUnderstandAPI, "understand/")
policy_api.add_resource(PolicyRecommendAPI, "recommend/")

# def policy_understand():
#     pass
