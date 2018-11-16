# coding=utf-8
from py2neo import Node, NodeMatcher

from data_management.models import BaseInterface, UUID, graph_

SubjectType = ["Norm", "Null", "Requirement"]


class Subject(BaseInterface):
    @classmethod
    def create(cls, subject_type, **kwargs):
        if subject_type not in SubjectType:
            raise Exception(f"subject_type must in {SubjectType}")
        node = Node(cls.__name__, subject_type, id=UUID(), **kwargs)
        cls.create = graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, *args, **kwargs):
        for arg in args:
            if arg not in SubjectType and arg != cls.__name__:
                raise Exception(f"label must in {SubjectType,cls.__name__}")
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
