# coding=utf-8
from collections import defaultdict
from condition_identification.args import NUMS, ADDRESS,FILTED_FIELD
from condition_identification.util.specialcondition_identify import idf_quantifiers, idf_address
from data_management.api.filtered_values import get_filtered_values
from data_management.api.field_info import list_all_field_name
from condition_identification.util.similarity_calculation import value_compare_similarity
from condition_identification.util.string_process import cmp_stringlist
from data_management.api.filtered_values_storage import filtered_values_store
class Value(object):
    """单例value类

    对于一个value值，找到他的value,数字，地址或者是与数据库某一列值（field)相似度很高
    单例模式可以大大减少数据库读取操作和内存消耗，不用每次都从数据库读取数据

    Attributes：
        values:  dict , {str:set}数据库field 与其值组成的字典
        value_filed:   dict , 对某个数据值，利用相似性判读建立起的它的值 与 field 的对应

    Example：{ "广州市南沙区黄阁镇境界大街22-1号地下室":["地址"],
            5千万元":['纳税总额','注册资本','营业总收入']}
    """
    def __init__(self, bc):
        self.bert_client = bc
        self.values_filed = defaultdict(list)
        self.filed_names = list_all_field_name()
        self.values_encode={}


    def construct_value_filed(self, regs):
        """对政策条件抽取出的关键词建立value_dict

         利用是否是数字 地址和与数据库数据相似度比较对政策申请条件关键词regs建立value_dict

         Args:
             regs:list ，政策文本关键词
                 Examples: ['工商注册地', '征管关系', '统计关系', '广州市南沙区范围内']

         Returns:
             value_dict :dict
                 Examples:
                     {'广州市南沙区范围内': ['地址']}

        """
        print(__name__)
        for line in regs:
            # 先判断是否是 地址或者数字
            if idf_quantifiers(line):
                self.values_filed[line] = NUMS
            elif idf_address(line):
                self.values_filed[line] = ADDRESS
            else:        # 非数字和地址 就用相似度来判断
                candidate_value = []
                line_word = line
                line_encode = self.bert_client.encode(line_word)

                # 如果发现过滤后的列名和给的列名有不一致，则自动重新更新
                if not cmp_stringlist(self.filed_names,get_filtered_values(FILTED_FIELD)['values']):
                    filtered_values_store()

                for field in self.filed_names:    # 用每一个field 下的value值与其做相似性判断
                    value_word = get_filtered_values(field)
                    if value_word is None or field in NUMS or field in ADDRESS:
                        continue
                    else:
                        value_word = value_word['values']
                    if field in self.values_encode:
                        value_encode = self.values_encode[field]
                    else:
                        value_encode = self.bert_client.encode(value_word)
                        self.values_encode[field] = value_encode
                    is_similar = value_compare_similarity(line_word, line_encode, value_word, value_encode)
                    if is_similar:      # 满足相似度要求
                        candidate_value.append(field)
                if candidate_value:
                    self.values_filed[line] = candidate_value
        return self.values_filed



if __name__ == '__main__':
    print(list_all_field_name())
    print(get_filtered_values('经营状态'))
    print(cmp_stringlist(list_all_field_name(),get_filtered_values(FILTED_FIELD)['values']))


