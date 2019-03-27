# coding=utf-8

from bert_serving.client import BertClient

from condition_identification.name_entity_recognition.args import *
from condition_identification.name_entity_recognition.extract import *
from condition_identification.name_entity_recognition.field import Field
from condition_identification.name_entity_recognition.search import *
from condition_identification.name_entity_recognition.value import Value
from condition_identification.name_entity_recognition.vectorize.extract_feature import BertVector


def get_field_value(word):
    if MODE == 'bert-util':
        bc = BertVector()
    else:
        bc = BertClient()
    keyword = extract_keyword(word, 2)
    field = Field(FILEPATH + '/field.txt')
    fielddict = field.construct_field_dict(keyword, bc)
    value = Value(FILEPATH + '/evalue')
    valuedict = value.construct_value_dict(keyword, bc)
    result = search_by_relative_pos(valuedict, fielddict, keyword)
    return result


if __name__ == '__main__':
    word = '纳税大于5千万；'
    print(get_field_value(word))
