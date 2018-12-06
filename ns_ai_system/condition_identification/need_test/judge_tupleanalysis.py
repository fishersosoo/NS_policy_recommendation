# coding=utf-8
import sys
import re
import os

sys.path.append("..")
try:
    from ..bonus_identify.Tree import DocTree
    from ..predicate_extraction.tuple_bonus_recognize import TupleBonus
    from ..predicate_extraction.tuple_bonus_recognize import Bonus_Condition_Tree
except Exception:
    from bonus_identify.Tree import DocTree
    from predicate_extraction.tuple_bonus_recognize import TupleBonus
    from predicate_extraction.tuple_bonus_recognize import Bonus_Condition_Tree

from syntax_analysis.sentence_analysis import HanlpSynataxAnalysis

def test_subtree(text):
    tree=DocTree()
    tree.construct(text)


    dict_dir=r"I:\NS_policy_recommendation\res\word_segmentation"
    tuplebonus = TupleBonus(dict_dir)
    pytree = tree.get_bonus_tree()


    tuplebonus.bonus_tuple_analysis(pytree)
    bonus_tree = tuplebonus.get_bonus_tree()
    bonus_tree.show()
    # for node in bonus_tree.all_nodes():
    #     print(bonus_tree.get_node_type(node))
    #     print(bonus_tree.get_node_content(node))

def test_tupleextract(sentence):
    tuple_bonus = TupleBonus()
    try:
        res = tuple_bonus.tuple_extract(sentence)
        print(res)

    finally:
        pass

if __name__ == "__main__":
    #synataxanalysis = HanlpSynataxAnalysis()
    #synataxanalysis.reloadHanlpCustomDictionary(r'I:\NS_policy_recommendation\res\word_segmentation')
    #sentence = '税务征管关系及统计关系在广州市南沙区范围内'
    #
    #test_tupleextract(sentence)


    filename = r'C:\Users\edward\Desktop\10.txt'
    tree = DocTree()
    tree.construct(filename)

    t=tree.get_bonus_tree()

    tuplebonus = TupleBonus()
    tuplebonus.bonus_tuple_analysis(t)
    tuplebonus.get_bonus_tree().show()

