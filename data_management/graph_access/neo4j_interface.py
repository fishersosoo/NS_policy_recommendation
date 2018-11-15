# coding=utf-8
"""访问neo4j数据库"""
from uuid import uuid1

from py2neo import Graph, Node, Relationship, NodeMatcher

# from data_management.models.object_ import Object
from data_management.models.object_ import Object
from data_management.models.predicate import Predicate
from data_management.models.requirement import Requirement,SubRequirement
# from data_management.models.subject import Subject
from data_management.models.subject import Subject


class Neo4jInterface:
    def __init__(self, **kwargs):
        self._graph = Graph(**kwargs)


if __name__ == "__main__":
    c = Neo4jInterface(host="cn.fishersosoo.xyz", user="neo4j", password="1995")
    g=c._graph
    # r = Requirement()
    # s=Subject('norm',"收入")
    # p=Predicate(value=">=")
    # o=Object('literal',"1000万元")
    # print(s.__node__)
    # r.subject.add(s)
    # r.object_.add(o)
    # r.predicate.add(p)
    # g.push(r)
    r=Requirement.match(g).first()
    r.subject
    print(r.__node__)
    # s = c.create_subject("requirement")
    # print(s.__node__)
    # s_2 = c.create_subject("norm", "收入")
    # s_2.in_requirement.add(s)
    # c._graph.push(s_2)

    # print(r)
    # c.
    # # r.__class__=Object
    # r=Object.wrap(r.__node__)
    # print(r)
    # c._graph.push(r)
    # print(r.__node__)
    # o=Object(Requirement)
    # graph = c._graph
    # subject
    # subject.__s=UUID()
    # for i in range(10):
    #     subject = Subject()
    #     subject.norm = "收入"
    #     print(subject)
    #     graph.push(subject)
    # print(subject.__node__)

    # for s in Subject.match(graph):
    #     print(s)
    #     graph.delete(s)
    # a = Node('Person', name='Alice')
    # b = Node('Person', name='Bob')
    # r = Relationship(a, 'KNOWS', b)
    # s = a | b | r
    # print(c.graph.create(s))

    # matcher = NodeMatcher(c.graph)
    # person = matcher.match("Person")
    # for one in person:
    #     print(one)
    #     c.graph.delete(one)
    # print(person)
    # c.close()
