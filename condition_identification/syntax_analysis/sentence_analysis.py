# coding=utf-8
from collections import namedtuple
from pyhanlp import *
import os

word_entity = namedtuple('word_entity', ['order','word','category'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S','P','O'])
syntax_tuple = namedtuple('syntax_tuple',['LEMMA','DEPREL','HEADLEMMA'])

class HanlpSynataxAnalysis:
    def __init__(self):
        pass
    #调用HanLp的句子依存分析,返回保存依存关系的元组供抽取类作分析
    def parseDependency(self,sentence):
        parseresult = HanLP.parseDependency(sentence)
        word_array = parseresult.getWordArray()
        syntax_tuples = []
        for word in word_array:
            syntax_tuples.append(syntax_tuple(LEMMA = word.LEMMA, DEPREL = word.DEPREL, HEADLEMMA = word.HEAD.LEMMA))
            #print("%s --(%s)--> %s" % (word.LEMMA, word.DEPREL, word.HEAD.LEMMA))
        return syntax_tuples

if __name__ == "__main__":
    synataxanalysis = HanlpSynataxAnalysis()
    entity = [word_entity(order='16', word='营业收入', category='norm'), word_entity(order='17|18', word='1亿元', category='number')]
    sentence = '②其他先进制造业：上一年度纳入我区统计核算的营业收入超过5亿元'
    sentence2 = '世界1000强企业属于大型企业'
    try:
        res = synataxanalysis.parseDependency(sentence2)
        print('\n')

    finally:
        pass