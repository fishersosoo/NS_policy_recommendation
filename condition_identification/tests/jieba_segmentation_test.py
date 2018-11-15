# coding=utf-8
from condition_identification.tests.document_parsing_test import test_html_parser
from condition_identification.word_segmentation.jieba_segmentation import Segmentation
from condition_identification.document_parsing.html_parser import HtmlParser


def test_cut():
    dict_path=r'Y:\Nansha AI Services\condition_identification\res\word_segmentation\dict'
    segmentation = Segmentation(dict_path)
    sentences = test_html_parser()
    for sentence in sentences:
        words = segmentation.cut(sentence)
        print('|'.join(words))

#
# if __name__ == "__main__":
#     test_cut()
