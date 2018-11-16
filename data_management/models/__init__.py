from abc import ABCMeta, abstractmethod
from uuid import uuid1

from py2neo import Graph, NodeMatcher

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


if __name__ == "__main__":
    g = Graph(host="cn.fishersosoo.xyz", user="neo4j", password="1995")
    # g.get
    # # p = PolicyGraphObject("Subject", "Requirement", x=1)
    # # # print(p)
    # # # p.save(g)
    # # # print(p)
    for i in range(10):
        p = PolicyGraphObject.find(g)[0]
        print(p)
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
