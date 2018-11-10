# coding=utf-8
from collections import namedtuple
from pyhanlp import *
import os

word_entity = namedtuple('word_entity', ['order','word','category'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S','P','O'])

class HanlpSynataxAnalysis:
    def __init__(self):
        pass
    #调用HanLp的句子依存分析
    def parseDependency(self,sentence):
        return HanLP.parseDependency(sentence)

    #传入单个句子，以及句子中识别出的实体，获取该句子中存在的政策条件三元组（S,P,0）
    def predicate_extraction(self,sentence,entity):
        res = self.parseDependency(sentence).getWordArray()
        entity_array = []
        for ents in entity:
            entity_array.append(ents.word)
        #print(entity_array)

        keyword = ""

        for word in res:
            if word.DEPREL == "核心关系" :
                keyword = word.LEMMA

        s_array = []
        o_array = []

        for word in res:
            if word.DEPREL == "主谓关系" and word.HEAD.LEMMA == keyword:
                s_array.append(word.LEMMA)
            elif word.DEPREL == "动宾关系" and word.HEAD.LEMMA == keyword:
                o_array.append(word.LEMMA)
        if len(s_array) == 0:
            s_array.append("NONE")

        if len(o_array) == 0:
            o_array.append("NONE")

        return three_tuple_entity(S=s_array[0], P=keyword, O=o_array[0])


if __name__ == "__main__":
    synataxanalysis = HanlpSynataxAnalysis()
    entity = [word_entity(order='16', word='营业收入', category='norm'), word_entity(order='17|18', word='1亿元', category='number')]
    sentence = '①现代物流业：上一年度纳入我区统计核算的营业收入6000万元以上;上一年度在我区纳税总额不低于1000万元。'
    try:
        sentences = sentence.split(';')
        for one_sentence in sentences:
            res = synataxanalysis.predicate_extraction(one_sentence,entity)
            print(res)
    finally:
        pass