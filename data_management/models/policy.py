# coding=utf-8
from py2neo import Node, NodeMatcher

from data_management.models import graph_, BaseInterface, UUID


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




if __name__ == "__main__":
    id = Policy.create(content="广州南沙新区_自贸片区_促进总部经济发展扶持办法.txt")
    print(Policy.find_by_id(id))
    Policy.update_by_id(id, content="广州南沙新区（自贸片区）集聚人才创新发展的若干措施｜广州市南沙区人民政府.txt")
    print(Policy.find_by_id(id))
    Policy.remove_by_id(id)
    print(Policy.find_by_id(id))
