# coding=utf-8
from collections import namedtuple

import jieba
import jieba.posseg


class Segmentation:
    def __init__(self, dict_path=None):
        self._tokenizer = jieba.Tokenizer()
        if dict_path is not None:
            self._tokenizer.load_userdict(dict_path)
        self._posseg = jieba.posseg.POSTokenizer(self._tokenizer)

    def cut(self, sentence):
        """
        将句子分词
        :param sentence:
        :return:
        """
        return self._tokenizer.cut(sentence)

    def psegcut(self,sentence):
        """
        将句子分词并标明词性
        :param sentence:
        :return:
        """
        return self._posseg.cut(sentence)

    def mark(self, sentence):
        pass

    @property
    def tokenizer(self):
        return self._tokenizer
