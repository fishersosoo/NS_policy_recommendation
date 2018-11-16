# coding=utf-8

from py2neo import Node, NodeMatcher

from data_management.models import BaseInterface, graph_, UUID

PredicateValue = ["&", "|", "<=", "<", ">", ">=", "==", "IS", "HAS"]


class Predicate(BaseInterface):
    @classmethod
    def create(cls, **kwargs):
        if kwargs.get("value", None) not in PredicateValue:
            raise Exception(f"predicate value must in {PredicateValue}")
        node = Node(cls.__name__, id=UUID(), **kwargs)
        cls.create = graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, **kwargs):
        if kwargs.get("value", None) not in PredicateValue:
            raise Exception(f"predicate value must in {PredicateValue}")
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        else:
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
