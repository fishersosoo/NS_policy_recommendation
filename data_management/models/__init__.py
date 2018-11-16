from abc import ABCMeta, abstractmethod
from uuid import uuid1

from py2neo import Node, Graph, NodeMatcher

from data_management.config import neo4j_config

graph_ = Graph(**neo4j_config)

UUID =lambda :str(uuid1())


class BaseInterface:
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def create(cls, **kwargs): pass

    @classmethod
    @abstractmethod
    def update_by_id(cls, id_, **kwargs): pass

    @classmethod
    @abstractmethod
    def remove_by_id(cls, id_): pass

    @classmethod
    @abstractmethod
    def find_by_id(cls, id_): pass


class PolicyGraphObject(Node):
    def __init__(self, *labels, **properties):
        if "_id" not in properties:
            properties["_id"] = str(uuid1())
        super().__init__(*labels, **properties)

    @property
    def id(self):
        return self["_id"]

    @id.setter
    def id(self, id_):
        self["_id"] = id_

    @classmethod
    def find(cls, graph, *labels, **properties):
        matcher = NodeMatcher(graph)
        nodes = matcher.match(*labels, **properties)
        results = []
        for node in nodes:
            # print(node.__uuid__)
            results.append(cls.from_node(node))
        return results

    @classmethod
    def from_node(cls, node):
        result = cls(*node.labels, **node)
        result.identity = node.identity
        result.__uuid__ = node.__uuid__
        # print(result.__uuid__)
        return result

    def create_node(self, graph):
        graph.create(self)

    def update_to_graph(self, graph):
        # s=Subgraph([self])
        s = self
        graph.push(s)

    def update_from_graph(self, graph):
        matcher = NodeMatcher(graph)
        node = matcher.match(*self.labels, **self).first()
        node = self.from_node(graph.pull(self))


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
