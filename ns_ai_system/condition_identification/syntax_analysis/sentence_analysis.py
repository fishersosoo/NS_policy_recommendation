# coding=utf-8
import re
from collections import namedtuple
from os import path

from pyhanlp import *

word_entity = namedtuple('word_entity', ['order', 'word', 'category', 'len', 'ordercount'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S', 'P', 'O'])
syntax_tuple = namedtuple('syntax_tuple', ['LEMMA', 'DEPREL', 'HEADLEMMA', 'POSTAG', 'HEAD'])


class HanlpSynataxAnalysis:
    def __init__(self):
        pass

    # 调用HanLp的句子依存分析,返回保存依存关系的元组供抽取类作分析
    def sentencePreprocessing(self, sentence):
        over_list = [i.start() for i in re.finditer('以上', sentence)]
        below_list = [i.start() for i in re.finditer('以下', sentence)]
        for j in over_list:
            i = j
            flag = False
            case_digit = 0
            search_window = 10
            while case_digit != 2 and i>j-search_window:
                if str(sentence[i - 1]).isdigit():
                    case_digit = 1
                elif case_digit == 1:
                    flag = True
                    case_digit = 2
                i = i - 1
                if i == 0:
                    break
            if flag == True:
                sentence = sentence[0:i + 1] + "超过" + sentence[i + 1:j] + sentence[j + 2:]
                # print(sentence)
        for j in below_list:
            i = j
            flag = False
            case_digit = 0
            search_window = 10
            while case_digit != 2 and i>j-search_window:
                if str(sentence[i - 1]).isdigit():
                    case_digit = 1
                elif case_digit == 1:
                    flag = True
                    case_digit = 2
                i = i - 1
                if i == 0:
                    break
            if flag == True:
                sentence = sentence[0:i + 1] + "低于" + sentence[i + 1:j] + sentence[j + 2:]

        return sentence

    def parseDependency(self, sentence):
        sentence = self.sentencePreprocessing(sentence)
        parseresult = HanLP.parseDependency(sentence)
        word_array = parseresult.getWordArray()
        syntax_tuples = []
        for word in word_array:
            # print(word)
            syntax_tuples.append(
                syntax_tuple(LEMMA=word.LEMMA, DEPREL=word.DEPREL, HEADLEMMA=word.HEAD.LEMMA, POSTAG=word.POSTAG,
                             HEAD=word.HEAD))
            # if str(word.POSTAG).strip() == "v":
            #print("%s --%s--> %s--> %s" % (word.LEMMA, word.DEPREL, word.HEAD.LEMMA,word.POSTAG))
        # print(syntax_dict)
        return syntax_tuples

    def reloadHanlpCustomDictionary(self, dict_path):

        # custompath = sys.prefix + r"\Lib\site-packages\pyhanlp\static\data\dictionary\custom\CustomDictionary.txt"

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

        # f = open(custompath, 'a', encoding='utf-8')
        # print(dicts)
        CustomDictionary = JClass("com.hankcs.hanlp.dictionary.CustomDictionary")

        try:
            for dict_dir in dicts:

                with open(dict_dir, 'r', encoding='utf-8') as fl:
                    word = fl.readline()

                    while word != "":
                        # print(word.strip())
                        # f.write('\n'+word.strip() )
                        CustomDictionary.add(word.strip())

                        word = fl.readline()
        except FileNotFoundError:
            print("FileNotFoundError")

        finally:
            # f.close()
            fl.close()
        CustomDictionary.reload()


if __name__ == "__main__":
    # #CustomDictionary.reload()
    synataxanalysis = HanlpSynataxAnalysis()
    # synataxanalysis.reloadHanlpCustomDictionary(r'I:\NS_policy_recommendation\res\word_segmentation')


    sentence2 = '（二）企业申报当年须是区内规模以上工业企业'
    try:
        res = synataxanalysis.parseDependency(sentence2)
        print(res)

    finally:
        pass
