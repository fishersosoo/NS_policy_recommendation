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
    return triples,all_sentence



