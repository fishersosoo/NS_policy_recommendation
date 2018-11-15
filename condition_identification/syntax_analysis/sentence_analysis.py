# coding=utf-8
from collections import namedtuple
from pyhanlp import *
import os

word_entity = namedtuple('word_entity', ['order','word','category','len','ordercount'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S','P','O'])
syntax_tuple = namedtuple('syntax_tuple',['LEMMA','DEPREL','HEADLEMMA'])

class HanlpSynataxAnalysis:
    def __init__(self):
        pass
    #调用HanLp的句子依存分析,返回保存依存关系的元组供抽取类作分析
    def sentencePreprocessing(self,sentence,entitys):

        length = len(entitys)
        curlen = 0
        for i,entity in enumerate(entitys):
            if i+1 <length:
                if entity.category == "norm" and int(entitys[i+1].order) == int(entity.order)+1:
                    sentence = sentence[0:entitys[i+1].len] +"在"+sentence[entitys[i+1].len:]
                    #print(sentence)
        return sentence

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
    entity = [word_entity(order='16', word='营业收入', category='norm',len=1,ordercount = 4), word_entity(order='17', word='1亿元', category='number',len=2,ordercount = 3)]
    sentence = '教育、卫生、文化、创意、体育、娱乐业和其他服务业：上一年度纳入我区统计核算的营业收入5000万元以上；且上一年度在我区纳税总额不低于1000万元'
    sentence2 = '专业服务业：上一年度纳入我区统计核算的营业收入在1亿元以上'
    try:
        #presentence = synataxanalysis.sentencePreprocessing(sentence,entity)
        res = synataxanalysis.parseDependency(sentence2)
        print(res)

    finally:
        pass