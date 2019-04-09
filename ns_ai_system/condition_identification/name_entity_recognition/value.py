# coding=utf-8
from collections import defaultdict
from pyhanlp import *
from condition_identification.name_entity_recognition.args import NUMS,ADDRESS
from condition_identification.util.specialcondition_identify import idf_nums,idf_address
from data_management.api import get_value_dic
from condition_identification.util.similarity_calculation import compare_similarity


class Value(object):
    """value类

    对于一个value值，找到他的value,数字，地址或者是与数据库某一列值（field)相似度很高
    Attributes：
        values:  dict , {str:set}数据库field 与其值组成的字典
        value_dict:   dict , 对某个数据值，利用相似性判读建立起的它的值 与 field 的对应


    Example：{ "广州市南沙区黄阁镇境界大街22-1号地下室":["地址"],
            5千万元":['纳税总额','注册资本','营业总收入']}
    """
    def __init__(self,bc):
        """用数据库里的值初始化values

        """
        self.values = self._get_value()
        self.value_dict = defaultdict(list)
        self.bert_client = bc

    def _get_value(self):
        """从数据库获取value

        各个字段处理后的value的字典

        Returns:
              values : dict, value值和他对应的field
              example:  {"企业基本信息_地址":["广州市南沙区金隆路26号1402房"],"企业基本信息_经营业务范围":["航空项目"]}

        """
        values = defaultdict(set)
        value_dic = get_value_dic()
        for key in value_dic:
            values_set = set(value_dic[key])
            values[key] = values_set
        return values

    def construct_value_dict(self, regs):
        """建立value_dict

         利用是否是数字 地址和相似度对regs建立value_dict


         Args:
             regs:list
             bc: bert 词向量工具
         Returns:
             value_dict :dict

        """
        print(__name__)
        for line in regs:
            # 先判断是否是 地址或者数字
            if idf_nums(line):
                self.value_dict[line] = NUMS
            elif idf_address(line):
                self.value_dict[line] = ADDRESS
            else:        # 非数字和地址 就用相似度来判断
                candidate_value = []
                for field in self.values:    # 用每一个field 下的value值与其做相似性判断
                    if field in NUMS or field in ADDRESS:
                        continue
                    values = self.values[field]
                    is_similar=compare_similarity(line, values, self.bert_client)
                    if is_similar:      # 满足相似度要求
                        candidate_value.append(field)
                if candidate_value:
                    self.value_dict[line] = candidate_value
        return self.value_dict

    def get_value_dict(self):
        """ 获取value_dic"""
        return self.value_dict

if __name__ == '__main__':
    # print(idf_nums('30岁'))
    print(Value.idf_address("南沙区"))

