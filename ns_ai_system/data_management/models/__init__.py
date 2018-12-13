from abc import ABCMeta, abstractmethod
from uuid import uuid1

from py2neo import Graph, NodeMatcher, RelationshipMatcher

from data_management.config import neo4j_config

graph_ = Graph(**neo4j_config)

UUID = lambda: str(uuid1())


class BaseInterface:
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def create(cls, **kwargs):
        pass

    @classmethod
    def update_by_id(cls, id_, *args, **kwargs):
        node = NodeMatcher(graph_).match(id=id_).first()
        if node is None:
            raise Exception(f"node {id_} not found")
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
    def clear(cls):
        for node in NodeMatcher(graph_).match(cls.__name__):
            for relationship in RelationshipMatcher(graph_).match({node}):
                graph_.separate(relationship)
            graph_.delete(node)

    @classmethod
    def find_by_id(cls, id_):
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            return [], dict(), None
        return node.labels, dict(**node), node

    @classmethod
    def find_by_id_in_graph(cls, id_):
        node = NodeMatcher(graph_).match(id=id_).first()
        if node is None:
            return [], dict(), None
        return node.labels, dict(**node), node

    @classmethod
    def find(cls, *args, **kwargs):
        nodes = NodeMatcher(graph_).match(*args, **kwargs).all()
        for node in nodes:
            yield node.labels, dict(**node), node


if __name__ == "__main__":
    pass
    g = Graph(host="cn.fishersosoo.xyz", user="neo4j", password="1995")
    # g.get
    # # p = PolicyGraphObject("Subject", "Requirement", x=1)
    # # # print(p)
    # # # p.save(g)
    # # # print(p)
    # for i in range(10):
    #     p = PolicyGraphObject.find(g)[0]
    #     print(p)
    # p.update_from_graph(g)
    # print(p)
    # p.save(g)
    # a = 1
    # dict
    # a["a"] = 2
    # print(NodeMatcher(g).match("node")["1"])
    # Node().
    # p.save(g)
    # print()
    # g.begin(True).commit()
    # g.create()
