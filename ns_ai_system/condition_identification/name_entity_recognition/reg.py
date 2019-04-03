# coding=utf-8

from condition_identification.name_entity_recognition.args import *
from condition_identification.name_entity_recognition.extract import *
from condition_identification.name_entity_recognition.field import Field
from condition_identification.name_entity_recognition.search import *
from condition_identification.name_entity_recognition.value import Value
from condition_identification.name_entity_recognition.vectorize.bert_word2vec import bert_word2vec

def get_field_value(sentence):
    """获取语句的field

    获取一个字符串对应的field

    Args:
        sentence:str

    Returns:
        字典

    """
    bc = bert_word2vec
    keyword = extract_keyword(sentence, 2)
    keyword = extract_address(keyword)
    field = Field()
    field_dict = field.construct_field_dict(keyword, bc)
    value = Value()
    value_dict = value.construct_value_dict(keyword, bc)
    result = search_by_relative_pos(value_dict, field_dict, keyword)
    return result


if __name__ == '__main__':
    word = '申报单位为创业投资基金的管理机构，管理机构及其运营的创业投资基金均注册在南沙，管理机构和所运营的创业投资基金须在中国证券投资基金业协会备案登记'
    text='集聚境外创业企业不少于20家'
    print(get_field_value(text))
