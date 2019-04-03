# coding=utf-8
from condition_identification.name_entity_recognition.util import cos_sim
from condition_identification.name_entity_recognition.vectorize.bert_word2vec import bert_word2vec
from data_management.api import list_field_info


class Field(object):
    """field 类

    对于一个value值，找到他的field, 根据他与field值的相似度，
    找到相似度高的满足条件的field 建立 field_dic

    Attributes:
        field: list,field 组成的list
        field_dict: dict， 与某个词相似度最高的field

    """

    def __init__(self):
        import time
        self.field = self._get_field()
        self.field_vectors = bert_word2vec(self.field)
        self.field_vec_dict = dict()
        for field, vector in zip(self.field, self.field_vec_dict):
            self.field_vec_dict[field] = vector
        self.field_dict = {}

    @staticmethod
    def _get_field():
        """获取field

        从数据库获取field,返回field的集合

        Returns:
            field: set,field集合

        """
        # 获取field 信息

        field = set(list_field_info())
        return field

    def _compare_similarity(self, line, vector, bc):
        """找到相似度最高的field

        从候选field中找出与line相似度最高的field

        Args:
            line:str
            bc:获取词向量的工具

        Returns:
            max_value: float
            max_word: str

        """
        max_value = 0
        max_word = ''
        # 找出与line相似度最高的field 以及他们的相似度
        for word in self.field:
            flag = False
            for w in word:  # 至少要有一个字相同
                if w in line:
                    flag = True
                    break
            if flag:
                if word not in self.field_vec_dict:
                    word_vec = bc([word])
                else:
                    word_vec = self.field_vec_dict[word]
                value = cos_sim(vector, word_vec)  # 获取他们的相似度
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
        print(__name__)
        if len(regs) == 0:
            return self.field_dict
        regs_vector = bc(regs)
        for line, vector in zip(regs, regs_vector):
            max_value, max_word = self._compare_similarity(line, vector, bc)
            if max_word != '' and max_value > 0.945:  # 有与它最相近的field 并且他们的 相似度满足要求
                self.field_dict[line] = max_word
        return self.field_dict

    def get_field_dict(self):
        """ 获取field_dict"""
        return self.field_dict
