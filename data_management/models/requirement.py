# coding=utf-8
from py2neo import NodeMatcher, Node

from data_management.models import BaseInterface, UUID, graph_


class Requirement(BaseInterface):
    @classmethod
    def create(cls, **kwargs):
        node = Node(cls.__name__, id=UUID(), **kwargs)
        cls.create = graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_,*args, **kwargs):
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        else:
            node.labels.update(args)
            node.update(kwargs)
        graph_.push(node)



if __name__=="__main__":
    Requirement.t()