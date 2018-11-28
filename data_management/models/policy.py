# coding=utf-8
from py2neo import Node, NodeMatcher, Relationship, Subgraph

from data_management.models import graph_, BaseInterface, UUID
from models.boon import Boon


class Policy(BaseInterface):
    @classmethod
    def create(cls, **kwargs):
        # kwargs["id"]=
        node = Node("Policy", id=UUID(), **kwargs)
        graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, **kwargs):
        node = NodeMatcher(graph_).match("Policy", id=id_).first()
        if node is None:
            raise Exception("policy not found")
        else:
            node.update(kwargs)
        graph_.push(node)

    @classmethod
    def add_boons(cls, id_, boons=None):
        if boons is None:
            boons = []
        _, _, policy = Policy.find_by_id(id_)
        # sub_graph = Subgraph(policy)
        boon_list = list(NodeMatcher(graph_).match("Boon").where(f"_.id in {boons}"))
        relationships=[]
        for boon in boon_list:
            relationships.append( Relationship(policy, "HAS_BOON", boon))
        sub_graph = Subgraph(boon_list+[policy],relationships)
        graph_.create(sub_graph)


if __name__ == "__main__":
    p_id = Policy.create(content="广州南沙新区_自贸片区_促进总部经济发展扶持办法.txt")
    b_id_1 = Boon.create(content="优惠1")
    b_id_2 = Boon.create(content="优惠2")
    Policy.add_boons(p_id, [b_id_1, b_id_2])
