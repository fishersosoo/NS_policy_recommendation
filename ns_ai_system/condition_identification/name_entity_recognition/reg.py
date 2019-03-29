# coding=utf-8
from bert_serving.client import BertClient
from condition_identification.name_entity_recognition.args import *
from condition_identification.name_entity_recognition.extract import *
from condition_identification.name_entity_recognition.Field import Field
from condition_identification.name_entity_recognition.search import *
from condition_identification.name_entity_recognition.Value import Value
from condition_identification.name_entity_recognition.vectorize.extract_feature import BertVector


def get_field_value(sentence):
    """获取语句的field

    获取一个字符串对应的field

    Args:
        sentence:str

    Returns:
        字典

    """
    if MODE == 'bert-util':    # 确定词向量的工具
        bc = BertVector()
    else:
        bc = BertClient()
    keyword = extract_keyword(sentence, 2)
    field = Field(FILE_PATH + '/field.txt')
    field_dict = field.construct_field_dict(keyword, bc)
    value = Value(FILE_PATH + '/evalue')
    value_dict = value.construct_value_dict(keyword, bc)
    result = search_by_relative_pos(value_dict, field_dict, keyword)
    return result


if __name__ == '__main__':
    word = '大于5千万元'
    print(get_field_value(word))
