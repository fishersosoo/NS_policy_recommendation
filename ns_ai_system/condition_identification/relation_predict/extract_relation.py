import re

from bert_serving.client import BertClient
from pyhanlp import *

from condition_identification.relation_predict.tensor_softmax import predict_relation


def get_lcs(string_1, string_2):
    """
    获得最长公共子序列的长度

    :param string_1:
    :param string_2:
    :return:
    """
    if not string_1 or not string_2:
        return 0
    string1_list = list(string_1)
    string2_list = list(string_2)
    lcs_list = []
    for i in range(len(string1_list)):
        flag = 0
        lcs = ''
        for j in range(i, len(string1_list)):
            for k in range(flag, len(string2_list)):
                if string1_list[j] == string2_list[k]:
                    lcs += string1_list[j]
                    flag = k + 1
        lcs_list.append((len(lcs), lcs))
    final_list = sorted(lcs_list, reverse=True)
    return final_list[0][0]


def extract_context(text, value):
    """
    以标点符号分隔开

    :param text:
    :param value:
    :return: str
    """
    sentences = re.split(r"[，；。？！]", text)
    for sentence in sentences:
        if value in sentence:
            return sentence
    words_in_value = HanLP.segment(value)
    for sentence in sentences:
        words_in_sentence = HanLP.segment(sentence)
        if all_in(words_in_value, words_in_sentence):
            return sentence
    return None


def all_in(words_in_value, words_in_sentence):
    """
    判断一个list里的元素是不是全部在另一个列表

    :param words_in_sentence:
    :param words_in_value:
    :return:
    """
    for word in words_in_value:
        if word not in words_in_sentence:
            return False
    return True


def get_relation(text, value):
    """

    :param text:
    :param value:
    :param bc: BertClient
    :return:
    """
    bc = BertClient()
    text = extract_context(text, value)
    if text:
        v = bc.encode([text])
        return predict_relation(v)
    else:
        return None


if __name__ == '__main__':
    text = "对于在我区新设的非总部型企业，上一年度在我区纳税总额500万元以上，且上一年度营业收入同比增长10%以上的；对于在我区已设立的非总部型企业，上一年度在我区纳税总额500万元以上，且上一年度营业收入同比增长10%以上的。"
    print(extract_context(text, '新设非总部型企业'))

