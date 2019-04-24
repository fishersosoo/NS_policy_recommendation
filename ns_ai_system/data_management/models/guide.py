# coding=utf-8
import datetime

import gridfs
from py2neo import Node, Relationship, NodeMatcher, Subgraph

from data_management.config import  py_client
from data_management.models import BaseInterface, UUID, graph_
from data_management.models.policy import Policy


class Guide(BaseInterface):
    @classmethod
    def find_leaf_requirement(cls, id_):
        """
        寻找政策最底层的requirement
        :param id_:
        :return:
        """
        ql = """
        MATCH
          path = (guide:Guide{id:{id_}})-[*]->(requirement:Requirement)
        UNWIND relationShips(path) AS r
        WITH collect(DISTINCT endNode(r))   AS endNodes, 
             collect(DISTINCT startNode(r)) AS startNodes
        UNWIND endNodes AS leaf
        WITH leaf WHERE NOT leaf IN startNodes
        RETURN leaf
        """
        return list(graph_().run(ql, parameters=dict(id_=id_)))

    @classmethod
    def list_valid_guides(cls):
        """
        查找所有在有效日期内的指南
        :rtype: list[Node]
        :return: 指南节点
        """
        # now = datetime.datetime.now()
        # nodes = list(
        #     NodeMatcher(graph_).match(cls.__name__).where(effective_time_begin__gte=now, effective_time_end__lte=now))
        nodes = list(
            NodeMatcher(graph_()).match(cls.__name__))
        return nodes

    @classmethod
    def create(cls, guide_id, file_name, **kwargs):
        print(guide_id)
        node = Node(cls.__name__, id=UUID(), guide_id=guide_id, file_name=file_name, **kwargs)
        graph_().create(node)
        return node["id"]

    @classmethod
    def set_effective_time(cls, id_, begin, end):
        Guide.update_by_id(id_, effective_time_begin=begin, effective_time_end=end)

    @classmethod
    def find_by_guide_id(cls, guide_id):
        node = NodeMatcher(graph_()).match(cls.__name__, guide_id=guide_id).first()
        if node is None:
            return [],dict(),None
        return node.labels, dict(**node), node

    @classmethod
    def link_to_policy(cls, guide_id, policy_id):
        _, _, guide_node = Guide.find_by_guide_id(guide_id)
        _, _, policy_node = Policy.find_by_policy_id(policy_id)
        relationship = Relationship(guide_node, "BASE_ON", policy_node)
        sub_graph = Subgraph([guide_node, policy_node], [relationship])
        graph_().create(sub_graph)

    @classmethod
    def get_file(cls, filename):
        fs = gridfs.GridFS(py_client.ai_system, "guide_file")
        return fs.get_version(filename=filename)

    @classmethod
    def add_boons(cls, id_, boons=None):
        if boons is None:
            boons = []
        _, _, guide = Guide.find_by_id(id_)
        boon_list = list(NodeMatcher(graph_()).match("Boon").where(f"_.id in {boons}"))
        relationships = []
        for boon in boon_list:
            relationships.append(Relationship(guide, "HAS_BOON", boon))
        sub_graph = Subgraph(boon_list + [guide], relationships)
        graph_().create(sub_graph)
