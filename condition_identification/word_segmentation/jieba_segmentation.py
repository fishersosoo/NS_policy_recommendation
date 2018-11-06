# coding=utf-8
from collections import namedtuple

import jieba


class Segmentation:
    def __init__(self, dict_path=None):
        self._tokenizer = jieba.Tokenizer()
        if dict_path is not None:
            self._tokenizer.load_userdict(dict_path)

    def cut(self, sentence):
        """
        将句子分词
        :param sentence:
        :return:
        """
        return self._tokenizer.cut(sentence)

    def mark(self, sentence):
        pass

    @property
    def tokenizer(self):
        return self._tokenizer
