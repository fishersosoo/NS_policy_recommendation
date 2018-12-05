# coding=utf-8
from py2neo import Node, NodeMatcher

from models import BaseInterface, UUID, graph_


class Word(BaseInterface):
    """
    词典一个词
    """

    @classmethod
    def create(cls, type_, word, **kwargs):
        """
        往数据库中添加一个词典项
        :param word: 具体的词
        :param type_: 词的类型,目前有Predicate,Category,Norm,Qualification
        :param kwargs:
        :return:
        """
        node = Node(cls.__name__, type_, id=UUID(), word=word, **kwargs)
        graph_.create(node)
        return node["id"]

    @classmethod
    def list_all(cls, *args):
        """
        返回所有指定类型的词典项
        :return:
        """
        return [match for match in NodeMatcher(graph_).match(cls.__name__, *args)]
