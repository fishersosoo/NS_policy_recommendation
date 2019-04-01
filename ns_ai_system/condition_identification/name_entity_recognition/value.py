# coding=utf-8
import re
from collections import defaultdict
from pyhanlp import *
from condition_identification.name_entity_recognition.args import *
from condition_identification.name_entity_recognition.util import cos_sim
from data_management.api import get_value_dic
from condition_identification.api.database_parse import database_extract


class Value(object):
    """value类

    对于一个value值，找到他的value,数字，地址或者是与数据库某一列值（field)相似度很高
    Attributes：
        values:  dict , 数据库field 与其值组成的字典
        value_dict:   dict ,  对某个数据值，利用相似性判读建立起的它的值 与 field 的对应
                   example：{ "广州市南沙区黄阁镇境界大街22-1号地下室":["地址"],
                             "5千万元":['纳税总额','注册资本','营业总收入']}
    """
    def __init__(self):
        """用数据库里的值初始化values

        """
        self.values = self._get_value()
        self.value_dict = defaultdict(list)

    @staticmethod
    def _get_value():
        """从数据库获取value

        各个字段处理后的value的字典

        Returns:
              values : dict, value值和他对应的field
              example:  {"企业基本信息_地址":["广州市南沙区金隆路26号1402房"],"企业基本信息_经营业务范围":["航空项目"]}

        """
        values = defaultdict(set)
        value_dic = get_value_dic()
        for key in value_dic:
            values_set = set(database_extract(value_dic[key]))
            values[key] = values_set
        return values

    @staticmethod
    def compare_similarity(line, value, bc):
        """ 计算 比较相似度 找出相似度最高的

        利用bert获得词向量，计算相似度，找到相似度最高的那个

        Args:
            line:  str
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
        """建立value_dict

         利用是否是数字 地址和相似度对regs建立value_dict


         Args:
             regs:list
             bc: bert 词向量工具
         Returns:
             value_dict :dict

        """
        for line in regs:
            # 先判断是否是 地址或者数字
            if self.idf_nums(line):
                self.value_dict[line] = NUMS
            elif self.idf_address(line):
                self.value_dict[line] = ADDRESS
            else:        # 非数字和地址 就用相似度来判断
                candidate_value = []
                for field in self.values:    # 用每一个field 下的value值与其做相似性判断
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
# TODO %
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


if __name__ == '__main__':
    # print(idf_nums('30岁'))
    pass

