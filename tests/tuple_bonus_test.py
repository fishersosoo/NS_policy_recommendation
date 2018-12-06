# coding=utf-8
import sys
import re

from condition_identification.bonus_identify.Tree import DocTree
from condition_identification.predicate_extraction.tuple_bonus_recognize import TupleBonus
from condition_identification.syntax_analysis.sentence_analysis import HanlpSynataxAnalysis

sys.path.append("..")

def test_subtree():
    tree=DocTree()
    tree.construct('../bonus_identify/广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')


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

    synataxanalysis = HanlpSynataxAnalysis()
    synataxanalysis.reloadHanlpCustomDictionary(r'I:\NS_policy_recommendation\res\word_segmentation')
    sentence = '是外资企业：'

    test_tupleextract(sentence)
    #test_subtree()

