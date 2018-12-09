# coding=utf-8
from py2neo import Node, NodeMatcher, Relationship

from data_management.models import BaseInterface, UUID, graph_
from data_management.models.requirement import Requirement


class Boon(BaseInterface):
    @classmethod
    def create(cls, **kwargs):
        node = Node(cls.__name__, id=UUID(), **kwargs)
        graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, **kwargs):
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        else:
            node.update(kwargs)
        graph_.push(node)

    @classmethod
    def add_requirement(cls, id_, requirement_id):
        _, _, boon_node = Boon.find_by_id(id_)
        _, _, requirement_node = Requirement.find_by_id(requirement_id)
        relationship = Relationship(boon_node, "HAS_REQUIREMENT", requirement_node)
        graph_.create(relationship)


if __name__ == "__main__":
    r_id = Requirement.create()
    id = Boon.create(content="""四、实施高学历人才补贴
对新引进落户工作的全日制本科及以上学历、学士及以上学位人才发放住房补贴，其中本科生2万元，硕士研究生4万元，博士研究生6万元。""")
    Boon.add_requirement(id,r_id)
