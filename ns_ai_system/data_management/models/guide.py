# coding=utf-8
import gridfs
from py2neo import Node, Relationship, NodeMatcher, Subgraph

from data_management.config import mongodb
from data_management.models import BaseInterface, UUID, graph_
from data_management.models.policy import Policy


class Guide(BaseInterface):
    @classmethod
    def create(cls, guide_id, file_name, **kwargs):
        node = Node(cls.__name__, id=UUID(), guide_id=guide_id, file_name=file_name, **kwargs)
        graph_.create(node)
        return node["id"]

    @classmethod
    def find_by_guide_id(cls, guide_id):
        node = NodeMatcher(graph_).match(cls.__name__, guide_id=guide_id).first()
        return node.labels, dict(**node), node

    @classmethod
    def link_to_policy(cls, guide_id, policy_id):
        _, _, guide_node = Guide.find_by_guide_id(guide_id)
        _, _, policy_node = Policy.find_by_policy_id(policy_id)
        relationship = Relationship(guide_node, "BASE_ON", policy_node)
        graph_.create(relationship)

    @classmethod
    def get_file(cls, filename):
        fs = gridfs.GridFS(mongodb, "guide_file")
        return fs.get_version(filename=filename)

    @classmethod
    def add_boons(cls, id_, boons=None):
        if boons is None:
            boons = []
        _, _, guide = Guide.find_by_id(id_)
        boon_list = list(NodeMatcher(graph_).match("Boon").where(f"_.id in {boons}"))
        relationships = []
        for boon in boon_list:
            relationships.append(Relationship(guide, "HAS_BOON", boon))
        sub_graph = Subgraph(boon_list + [guide], relationships)
        graph_.create(sub_graph)
