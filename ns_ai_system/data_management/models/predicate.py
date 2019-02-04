# coding=utf-8

from py2neo import Node, NodeMatcher

from data_management.models import BaseInterface, graph_, UUID

PredicateValue = ["and", "or", "<=", "<", ">", ">=", "==", "IS", "HAS"]


class Predicate(BaseInterface):
    @classmethod
    def create(cls, **kwargs):
        # if kwargs.get("value", None) not in PredicateValue:
        #     raise Exception(f"predicate value must in {PredicateValue}")
        node = Node(cls.__name__, id=UUID(), **kwargs)
        graph_().create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, **kwargs):
        # if kwargs.get("value", None) not in PredicateValue:
        #     raise Exception(f"predicate value must in {PredicateValue}")
        node = NodeMatcher(graph_()).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        else:
            node.update(kwargs)
        graph_().push(node)
