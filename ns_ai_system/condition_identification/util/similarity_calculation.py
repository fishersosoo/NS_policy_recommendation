from pyhanlp import *
from condition_identification.util.distance_calculations import cos_sim
from condition_identification.util.string_process import getNumofCommonSubstr
def _search_max_word(value,value_encodes,line_encode,line):
    max_value = 0
    max_word = ''
    has_max_word=False
    for word, value_encode in zip(value, value_encodes):
        word = word.strip()
        flag = False
        for term in HanLP.segment(word):  # 必须要有相同的词才可以
            if term.word in line:
                flag = True
                break
        if flag:
            value = cos_sim(line_encode, value_encode)
            if max_value < value:
                max_value = value
                max_word = word
            if max_word != '' and max_value > 0.945:
                has_max_word = True
                break

    return has_max_word


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

    line_encode = bc.encode([line])
    # 先取前30个作一下比较
    if len(value) > 30:
        part_value_encodes = bc.encode(list(value)[0:30])
        has_max_word = _search_max_word(value, part_value_encodes, line_encode, line)

        if not has_max_word:
            rest_value_encodes = bc.encode(list(value)[30:])
            has_max_word = _search_max_word(value, rest_value_encodes, line_encode, line)
    else:
        all_value_encodes = bc.encode(list(value))
        has_max_word = _search_max_word(value, all_value_encodes, line_encode, line)
    return has_max_word





def field_compare_similarity(line, vector,field,field_vec_dict):
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
    for word in field:
        has_word_count=getNumofCommonSubstr(word,line)[1]
        if has_word_count>0:
            word_vec = field_vec_dict[word]
            value = cos_sim(vector, word_vec)  # 获取他们的相似度
            if max_value < value:
                max_value = value
                max_word = word
    return max_value, max_word