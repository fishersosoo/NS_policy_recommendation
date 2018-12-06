# coding=utf-8
import sys

from condition_identification.word_segmentation.jieba_segmentation import Segmentation

sys.path.append("..")
from tests.document_parsing_test import test_html_parser

def test_cut():
    dict_path=r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\dict'
    segmentation = Segmentation(dict_path)
    # sentences = test_html_parser()
    # for sentence in sentences:
    #     words = segmentation.cut(sentence)
    #     print('|'.join(words))
    words = segmentation.psegcut("1000万以上超过至以下不高于不低于")
    print(tuple(words))

if __name__ == "__main__":
     test_cut()
