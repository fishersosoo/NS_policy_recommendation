# coding=utf-8
from condition_identification.name_entity_recognition.util import cos_sim


class Field(object):
    """field 类

    对于一个value值，找到他的field, 根据他与field值的相似度，
    找到相似度高的满足条件的field 建立 field_dic

    Attributes:
        field: list,field 组成的list
        field_dic: dic， 跟他最接近的几个field


    """
    def __init__(self, field_file):
        """
        Args:
            field_file: 指代候选的字段所在的文件
        """
        self.field=self.__get_field(field_file)
        self.field_dict = {}

    @staticmethod
    def __get_field(field_file):
        """获取field

        从field_file文件读取field,返回field的集合

        Args:
            field_file:要读取的文件

        Returns:
            field的集合

        """
        field = set()
        with open(field_file, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if line!='':
                    field.add(line)
        return field

    def _compare_similarity(self, line, bc):
        """
       从候选field中找出与line相似度最高的field
        Args:
            line:str
            bc:获取词向量的工具
        Returns:
            最高的相似度值与对应的field
        """
        max_value = 0
        max_word = ''
        # 找出与line相似度最高的field 以及他们的相似度
        for word in self.field:
            word = word.strip()
            flag = False
            for w in word:  # 至少要有一个字相同
                if w in line:
                    flag = True
                    break
            if flag:
                value = cos_sim(bc.encode([line]), bc.encode([word]))  # 获取他们的相似度
                if max_value < value:
                    max_value = value
                    max_word = word
        return max_value, max_word

    def construct_field_dict(self, regs, bc):
        """建立一个field 的字典

        利用相似度找出跟regs相似度最高且满足要求的field值

        Args:
            regs:list,
            bc:获取词向量的工具
        Returns：
             字典

        """
        for line in regs:
            max_value, max_word = self._compare_similarity(line, bc)
            if max_word != '' and max_value > 0.945:  # 有与它最相近的field 并且他们的 相似度满足要求
                self.field_dict[line] = max_word
        return self.field_dict

    def get_field_dict(self):
        """ 获取field_dict"""
        return self.field_dict


