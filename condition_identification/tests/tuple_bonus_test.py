# coding=utf-8
import sys
import re
sys.path.append("..")
try:
    from ..bonus_identify.Tree import DocTree
    from ..predicate_extraction.tuple_bonus_recognize import TupleBonus
except Exception:
    from bonus_identify.Tree import DocTree
    from predicate_extraction.tuple_bonus_recognize import TupleBonus

def test_subtree():
    tree=DocTree()
    tree.construct('../bonus_identify/广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')

    dict_dir=r"Y:\Nansha AI Services\condition_identification\res\word_segmentation"
    tuplebonus = TupleBonus(dict_path)

    #print(tuplebonus.tuple_extract("在我区纳税总额超过1000万元（含）的，奖励300万元"))

    tuplebonus.bonus_tuple_analysis(tree)
    tuplebonus.get_bonus_tree().show()


if __name__ == "__main__":
    test_subtree()

