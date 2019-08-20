# coding=utf-8
import json

from condition_identification.doctree_contruction.DocTree import *
from condition_identification.rdf_triple.triple_tree import constructTriple
from condition_identification.doctree_contruction.DocTreeOp import getTitle






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
        #TODO: 从原文中提取标题和条件并设置document对象对应属性
        if document.title is None:
            document.title = getTitle(text)
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
            self.OriginSentenceByPolicyLine = constructTriple(self._tree)
            return self.OriginSentenceByPolicyLine
