# coding=utf-8
import json

from condition_identification.doctree_contruction.DocTree import *
from condition_identification.rdf_triple.triple_tree import constructTriple


def paragraph_extract(text):
    """抽取指南

    根据指南的标题结构，抽取政策条件，并构造结构树

    Args：
        text: str 政策文本

    Returns：
        tree: Tree 构造后的政策树


    """
    doc_tree = DocTree()
    doc_tree.construct(text)
    tree = doc_tree.get_tree()
    return tree


def triple_extract(tree):
    """提取条件树

    根据传入的指南树进行filed,value,relation的拆分
    并且组装成and/or关系
    其主要关系图查看uml.jpg

    Args:
        tree: Tree 指南拆解后的树

    Returns:
        tree: Tree 对输入的tree的node内容进行改写结果
        all_sentence: dict {id:sentence} 所有政策条件句子
    """
    triples, all_sentence = constructTriple(tree)
    return triples, all_sentence


class Clause():
    """
    表示一个子句，一个子句有三元组对应。相当于原来的triple数据结构
    """

    def __init__(self, text=None, fields=None, relation=None, value=None):
        """
        Args:
            text: 原文
            fields: 可能的字段列表
            relation: 关系
            value: 值
        """
        if fields is None:
            fields = list()
        self.fields = fields
        self.text = text
        self.relation = None
        self.value = None

    def to_dict(self):
        return dict(fields=self.fields, text=self.text, relation=self.relation, value=self.value)


class Sentence():
    """
    表示原文中一个完整的条件。一个条件可能会包含有多个（逗号分割）子句
    """

    def __init__(self, text=None, clauses=None):
        """

        :param text: 原文
        :param clauses:
        """
        self.text = text
        if clauses is None:
            self.clauses = list()

    def to_dict(self):
        return dict(text=self.text, clauses=[one.to_dict() for one in self.clauses])


class Document:
    """
    表示一个指南文档，指南文档包括了多个条件语句和一个标题。
    """

    @classmethod
    def paragraph_extract(cls, text):
        """

        根据指南的标题结构，抽取政策条件，并构造结构树，并构造一个Document对象

        Args：
            text: str 政策文本

        Returns：
            tree: Tree 构造后的政策树


        """

        doc_tree = DocTree()
        doc_tree.construct(text)
        tree = doc_tree.get_tree()
        document = Document()
        document._tree = tree
        # TODO: 从原文中提取标题和条件并设置document对象对应属性
        if document.title is None:
            raise NotImplementedError()
        return document

    def __init__(self, title=None, sentences=None):
        """

        Args:
            title: 标题
            sentences: 条件列表
        """
        self._tree = None  # 用于保存树结构
        self.title = title
        if sentences is None:
            self.sentences = list()

    def triple_extract(self):
        if self._tree is not None:
            # TODO:解析sentences中的条件，拆分出子句并填充三元组信息
            raise NotImplementedError()

    def to_dict(self):
        return dict(title=self.title, sentences=[one.to_dict() for one in self.sentences])
