# coding=utf-8
import re
from collections import defaultdict
from pyhanlp import *
from condition_identification.name_entity_recognition.args import *
from condition_identification.name_entity_recognition.util import cos_sim


class Value(object):
    """value类

    对于一个value值，找到他的value,数字，地址或者是与数据库值相似度很高
    Attributes：
        field_values_map:  set(value）
        value_dic:
    """
    def __init__(self, value_file_dir):
        """用文件初始化value_dic

        Args:
             value_file_dir: str  value_file 路径

        """
        self.values = self.__get_value(value_file_dir)
        self.value_dict = defaultdict(list)

    @staticmethod
    def __get_value(value_file_dir):
        """从文件读取value的集合

        从指定目录的文件中加载各个字段处理后的value集合

        Args:
              value_file_dir: value文件目录

        Returns:
              value_dic

        """
        values = defaultdict(set)
        for file in os.listdir(value_file_dir):
            value_set = set()
            # 从文件中读取value值
            with open(os.path.join(value_file_dir, file), 'r', encoding='utf8') as f:
                for line in f:
                    line = line.strip()
                    if line != '':
                        value_set.add(line)
                values[file] = value_set
        return values

    @staticmethod
    def compare_similarity(line, value, bc):
        """ 计算 比较相似度 找出相似度最高的

        利用bert获得词向量，计算相似度，找到相似度最高的那个

      Args:
            line:str
            value： list
            bc: 获得词向量的bert 工具

      Returns:
          max_value:float  相似度最高的相似度值
          max_word：str    相似度最高的那个词
        """
        max_value = 0
        max_word = ''
        for word in value:
            word = word.strip()
            flag = False
            for term in HanLP.segment(word):   # 必须要有相同的词才可以
                if term.word in line:
                    flag = True
                    break
            if flag:
                value = cos_sim(bc.encode([line]), bc.encode([word]))
                if max_value < value:
                    max_value = value
                    max_word = word
        return max_value, max_word

    def construct_value_dict(self, regs, bc):
        """建立value_dic

         利用是否是数字 地址和相似度建立value_dic

         Args:
             regs:list
             bc: bert 词向量工具
         Returns:
             value_dic :dic

        """
        for line in regs:
            # 先判断是否是 地址或者数字
            if self.idf_nums(line):
                self.value_dict[line] = NUMS
            elif self.idf_address(line):
                self.value_dict[line] = ADDRESS
            else:        # 非数字和地址 就用相似度来判断
                candidate_value = []
                for field in self.values:
                    values = self.values[field]
                    max_value, max_word = self.compare_similarity(line, values, bc)
                    if max_word != '' and max_value > 0.945:      # 非空并且满足相似度要求
                        candidate_value.append(field)
                if candidate_value:
                    self.value_dict[line] = candidate_value
        return self.value_dict

    def get_filed_dict(self):
        """ 获取value_dic"""
        return self.value_dict

# TODO 这里应该放再抽关键字之前，因为有可能关键字没抽到
    @staticmethod
    def idf_nums(word):
        """判断是否是数字

        通过分词工具词性分析，判断数字

        Args:
            word:str

        Returns:
            True 或者 False

        """
        # 通过词法分析 根据词性判断
        b = HanLP.parseDependency(word)
        word_array = b.getWordArray()
        mflag = False
        qflag = False
        for word in word_array:
            if word.POSTAG == 'm':
                mflag = True
            if word.POSTAG == 'q':
                qflag = True
        if mflag and qflag:
            return True
        else:
            return False

# 数据库字段的地址就用地的相似度去找，
    @staticmethod
    def idf_address(sentence):
        """判断是否是地址

        判断是否是地址值，利用HanLP的地址识别

        Args:
            sentence:str

        Returns：
            True 或者 False

        """
        # 利用HanLP 接口识别是否是地址值
        segment = HanLP.newSegment().enablePlaceRecognize(False)
        term_list = segment.seg(sentence)
        natures = [str(i.nature) for i in term_list]
        if 'ns' in natures:
            return True
        else:
            return False

if __name__=='__main__':
    # print(idf_nums('30岁'))
    pass

