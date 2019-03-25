import numpy as np
from bert_serving.client import BertClient
import re
from relation_predict.tensor_softmax import predict_relation
from pyhanlp import *
####获得最长公共子序列的长度
def get_lcs(string1, string2):
    '''
    输入：待比较的两个字符串

    '''
    if not string1 or not string2:
        return 0
    string1_list = list(string1)
    string2_list = list(string2)
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
    final_list=sorted(lcs_list, reverse=True)
    return final_list[0][0]

#####窗口大小 或者以 标点符号 分隔开 或  分割 和?

def extract_context(text,value):
    '''

    :param text: sentence
    :param value: value []
    :param n: 窗口大小 这个暂时没有用到
    :return: str
    '''
    c = re.split(r"[，；。？！]", text)
    for i in c:
        if value in i:
            return i
    v=HanLP.segment(value)
    for i in c:
        s=HanLP.segment(i)
        if all_in(s,v):
            return i
    return None
    # return value
####判断一个list里的元素是不是全部在另一个列表,
def all_in(sentence,value):
    for v in value:
        if v not in sentence:
            return False
    return True


def get_relation(text,value):
    '''

    :param text:
    :param value:
    :param bc: BertClient
    :return:
    '''
    bc = BertClient()
    text=extract_context(text,value)
    if text:
        v=bc.encode([text])
        return predict_relation(v)
    else:
        return None


if __name__ == '__main__':

    # print(get_consine_similarity('申报单位注册地、税务征管关系及统计关系在广州市南沙区范围内',"在广州市南沙区",bc))
    text="对于在我区新设的非总部型企业，上一年度在我区纳税总额500万元以上，且上一年度营业收入同比增长10%以上的；对于在我区已设立的非总部型企业，上一年度在我区纳税总额500万元以上，且上一年度营业收入同比增长10%以上的。"
    print(extract_context(text,'新设非总部型企业'))
    # print(extract_context(text,['500万元以上','10%以上','500万元','10%以上']))
    # print(get_lcs(text,'500元以上'))
    # print(extract_context(text,'500万元以上'))
    # print(get_relation(text,'500万元以上',bc))

    # s=HanLP.segment('今天下雨吗')

