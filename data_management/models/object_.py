# coding=utf-8
from py2neo import Node, NodeMatcher

from data_management.models import BaseInterface, UUID, graph_

ObjectType = ["Requirement", "Category", "Qualification", "Literal"]


class Object(BaseInterface):
    @classmethod
    def create(cls, object_type, **kwargs):
        if object_type not in ObjectType:
            raise Exception(f"object_type must in {ObjectType}")
        node = Node(cls.__name__, object_type, id=UUID(), **kwargs)
        cls.create = graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, *args, **kwargs):
        for arg in args:
            if arg not in ObjectType and arg != cls.__name__:
                raise Exception(f"label must in {ObjectType,cls.__name__}")
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        else:
            node.labels.update(args)
            node.update(kwargs)
        graph_.push(node)

    @classmethod
    def remove_by_id(cls, id_):
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        graph_.delete(node)

    @classmethod
    def find_by_id(cls, id_):
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            return None, None
        return node.labels, dict(**node)
