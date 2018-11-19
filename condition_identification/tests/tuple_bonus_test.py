# coding=utf-8
import sys
import re
sys.path.append("..")

from bonus_identify.Tree import DocTree
from predicate_extraction.tuple_bonus_recognize import TupleBonus

def test_subtree():
    tree=DocTree('../bonus_identify/广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')
    tree.construct()
    tuplebonus = TupleBonus()

    #传入norm、category、qualification的路径进行词典配置，若不传入则默认使用库自带的三类词典
    tuplebonus.segementation_construct(r'I:\NS_policy_recommendation\res\word_segmentation')

    tuplebonus.bonus_tuple_analysis(tree)
    tuplebonus.get_bonus_tree().show()


if __name__ == "__main__":
    test_subtree()
