# coding=utf-8
from condition_identification.bonus_identify.Tree import DocTree
from condition_identification.predicate_extraction.tuple_bonus_recognize import TupleBonus

def construct_tupletree_by_file(filename):

    try:
        tree = DocTree()
        tree.construct(filename)
        t = tree.get_bonus_tree()
        tuplebonus = TupleBonus()
        tuplebonus.bonus_tuple_analysis(t)
        return tuplebonus.get_bonus_tree()

    finally:
        pass

def construct_tupletree_by_byte(byte):
    try:
        tree = DocTree()

        #   需要换成使用二进制流构建树的接口
        #   tree.construct(byte)
        #

        t = tree.get_bonus_tree()
        tuplebonus = TupleBonus()
        tuplebonus.bonus_tuple_analysis(t)
        return tuplebonus.get_bonus_tree()

    finally:
        pass


