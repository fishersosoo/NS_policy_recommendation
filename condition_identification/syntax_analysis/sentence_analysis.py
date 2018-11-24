# coding=utf-8
from collections import namedtuple
from pyhanlp import *
import sys
from os import path
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

    def reloadHanlpCustomDictionary(self,dict_path):
        custompath = sys.prefix + r"\Lib\site-packages\pyhanlp\static\data\dictionary\custom\CustomDictionary.txt"
        # print(path)
        dicts = []
        if dict_path is not None:
            dicts.append(path.join(dict_path, "norm_dict"))
            dicts.append(path.join(dict_path, "category_dict"))
            dicts.append(path.join(dict_path, "qualification_dict"))
        else:
            dicts.append(
                r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\norm_dict')
            dicts.append(
                r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\category_dict')
            dicts.append(
                r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\qualification_dict')

        f = open(custompath, 'a', encoding='utf-8')
        #print(dicts)
        try:
            for dict_dir in dicts:

                with open(dict_dir, 'r', encoding='utf-8') as fl:
                    word = fl.readline()

                    while word != "":
                        #print(word.strip())
                        f.write('\n'+word.strip() )
                        word = fl.readline()
        except FileNotFoundError:
            print("FileNotFoundError")

        finally:
            f.close()
            fl.close()
        #CustomDictionary.reload()

if __name__ == "__main__":
    #CustomDictionary.reload()
    synataxanalysis = HanlpSynataxAnalysis()
    #synataxanalysis.reloadHanlpCustomDictionary(r'I:\NS_policy_recommendation\res\word_segmentation')
    entity = [word_entity(order='16', word='营业收入', category='norm',len=1,ordercount = 4), word_entity(order='17', word='1亿元', category='number',len=2,ordercount = 3)]
    sentence = '教育、卫生、文化、创意、体育、娱乐业和其他服务业：上一年度纳入我区统计核算的营业收入高于5000万元；上一年度在我区纳税总额不低于1000万元'
    sentence2 = '对在南沙港区完成年度外贸集装箱吞吐量达到10万TEU的新落户船公司给予250万元的一次性奖励'
    try:
        #presentence = synataxanalysis.sentencePreprocessing(sentence,entity)
        res = synataxanalysis.parseDependency(sentence2)
        print(res)

    finally:
        pass