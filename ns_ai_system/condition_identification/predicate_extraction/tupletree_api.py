# coding=utf-8
from condition_identification.bonus_identify.DocTree import DocTree
from condition_identification.bonus_identify.DocTreeOp import get_handletime
from condition_identification.predicate_extraction.tuple_bonus_recognize import TupleBonus


def construct_tupletree_by_str(text):
    """

    :param text: 政策文档文本
    :return: 条件树结构，有效时间开始日期，有效时间结束日期
    """
    tree = DocTree()
    tree.construct(text, 2)
    t = tree.get_bonus_tree()
    tuplebonus = TupleBonus()
    tuplebonus.bonus_tuple_analysis(t)
    min_time, max_time=get_handletime(tree)
    return tuplebonus.get_bonus_tree(), min_time, max_time


def construct_tupletree_by_file(filename):
    try:
        tree = DocTree()
        tree.construct(filename, 1)
        t = tree.get_bonus_tree()
        tuplebonus = TupleBonus()
        tuplebonus.bonus_tuple_analysis(t)
        return tuplebonus.get_bonus_tree()

    finally:
        pass


def construct_tupletree_by_bytestr(byte):
    try:
        tree = DocTree()

        #   需要换成使用二进制流构建树的接口
        tree.construct(byte, 2)
        #

        t = tree.get_bonus_tree()
        tuplebonus = TupleBonus()
        tuplebonus.bonus_tuple_analysis(t)
        return tuplebonus.get_bonus_tree()

    finally:
        pass
