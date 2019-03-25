from pyhanlp import *
from name_entity_recognition.util import  cos_sim
from name_entity_recognition.args import *
from collections import defaultdict


import re
class Value(object):
    def __init__(self,valuefiledir):
        self.values = self.__get_Value(valuefiledir)
        self.value_dict = defaultdict(list)

    def __get_Value(self, valuefiledir):
        values = defaultdict(set)
        for file in os.listdir(valuefiledir):
            value_set=set()
            with open(os.path.join(valuefiledir, file), 'r', encoding='utf8') as f:
                for line in f:
                    line = line.strip()
                    if line!='':
                        value_set.add(line)
                values[file]=value_set
        return values

    def compare_similarity(self, line, value,bc):
        max_value = 0
        max_word = ''
        for word in value:
            word = word.strip()
            flag = False
            for term in HanLP.segment(word):
                if term.word in line:
                    flag=True
                    break
            if flag:
                value=cos_sim(bc.encode([line]),bc.encode([word]))
                if max_value<value:
                    max_value=value
                    max_word=word
        return max_value,max_word

    def constuct_valuedict(self, regs, bc):
        for line in regs:
            if self.idf_nums(line):
                self.value_dict[line]=NUMS
            elif self.idf_address(line):
                self.value_dict[line]=ADDRESS
            else:
                candidate_value=[]
                for key in self.values:
                    value=self.values[key]
                    max_value, max_word = self.compare_similarity(line, value,bc)
                    if max_word != '' and max_value > 0.945:
                        candidate_value.append(key)

                if candidate_value:
                    self.value_dict[line] = candidate_value
        return self.value_dict
    def get_fileddict(self):
        return self.value_dict



# TODO 还有中文的数字一二三四没有拆
# TODO 这里应该放再抽关键字之前，因为有可能关键字没抽到
    def idf_nums(self,word):
        p = r"\d*.*"
        pattern = re.compile(p)
        match = pattern.findall(word)[0]
        if match!='' and '元'in word:
            return True
        else:
            return False
# 数据库字段的地址就用地的相似度去找，
    def idf_address(self,sentence):
        segment = HanLP.newSegment().enablePlaceRecognize(False)
        term_list = segment.seg(sentence)
        natures=[str(i.nature) for i in term_list]
        if 'ns' in natures:
            return True
        else:
            return False

