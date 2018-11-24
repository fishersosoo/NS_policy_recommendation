# coding=utf-8
import sys
import re
sys.path.append("..")
try:
    from ..bonus_identify.Tree import DocTree
    from ..predicate_extraction.tuple_bonus_recognize import TupleBonus
    from ..predicate_extraction.tuple_bonus_recognize import Bonus_Condition_Tree
except Exception:
    from bonus_identify.Tree import DocTree
    from predicate_extraction.tuple_bonus_recognize import TupleBonus
    from predicate_extraction.tuple_bonus_recognize import Bonus_Condition_Tree
def test_subtree():
    tree=DocTree()
    tree.construct('../bonus_identify/test.txt')

    dict_dir=r"Y:\Nansha AI Services\condition_identification\res\word_segmentation"
    tuplebonus = TupleBonus()

    tuplebonus.bonus_tuple_analysis(tree)
    bonus_tree = tuplebonus.get_bonus_tree()
    for node in bonus_tree.all_nodes():
        print(bonus_tree.get_node_type(node))
        print(bonus_tree.get_node_content(node))

def test_tupleextract(sentence):
    tuple_bonus = TupleBonus()
    try:
        res = tuple_bonus.tuple_extract(sentence)
        print(res)

    finally:
        pass

if __name__ == "__main__":
    sentence = '对在南沙港区完成年度外贸集装箱吞吐量达到10万TEU的新落户船公司给予250万元的一次性奖励'
    test_tupleextract(sentence)

