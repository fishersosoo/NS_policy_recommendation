# coding=utf-8
from condition_identification.name_entity_recognition.extract_keyword import *
from condition_identification.name_entity_recognition.field import Field
from condition_identification.util.search import search_by_relative_pos
from condition_identification.name_entity_recognition.value import Value
from condition_identification.name_entity_recognition.vectorize.bert_word2vec import BertClient
from condition_identification.util.specialcondition_identify import extract_address
# from bert_serving.client import BertClient

def get_field_value(sentence):
    """获取语句的field

    获取一个字符串对应的field

    Args:
        sentence:str

    Returns:
        字典

    """
    bc = BertClient()
    keyword = extract_keyword(sentence, 2)
    keyword = extract_address(keyword)
    field = Field(bc)
    field_dict = field.construct_field_dict(keyword)
    value = Value(bc)
    value_dict = value.construct_value_dict(keyword)
    result,is_explicit_field = search_by_relative_pos(value_dict, field_dict, keyword)

    return result,is_explicit_field

if __name__ == '__main__':
    word = '申报单位为创业投资基金的管理机构，管理机构及其运营的创业投资基金均注册在南沙，管理机构和所运营的创业投资基金须在中国证券投资基金业协会备案登记'
    text='集聚境外创业企业不少于20家'
    print(get_field_value(text))
