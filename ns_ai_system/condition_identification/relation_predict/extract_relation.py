# coding=utf-8
import re
from condition_identification.util.specialcondition_identify import idf_address,idf_nums
from condition_identification.util.sentence_preprocess import preprocess
# 定义关键字
dayu = ['大于', '以上', '超过', '多于', '高于', '至多', '以后']
budayu = ['不' + x for x in dayu]
xiaoyu = ['小于', '以下', '少于', '低于', '至少', '未满', '以前']
buxiaoyu = ['不' + x for x in xiaoyu]
weiyu = ['位于', '区内', '范围内','在']
fou = ['无', '不']





def get_relation(sentence, word):
    """抽取条件

    根据关键字来判断条件

    Args:
        sentence: str 原句子
        word: str 实体词

    Returns:
        relation: str 关系
    """
    pre_sentence = preprocess(sentence, word)
    relation = relation_pre(pre_sentence, word)
    return relation,pre_sentence


def relation_pre(sentence, word):
    """ 关系抽取

    具体根据关键字抽取的逻辑

    Args:
        sentence: str 预处理后的句子
        word:  str 实体

    Returns:
        str:返回的具体关系值，判断不出的一律返回"是"
    """
    # 约束 数字和地址
    is_num = idf_nums(word)
    is_location = idf_address(word)
    relation='是'
    # 数字约束
    if is_num:
        for d in dayu:
            if d in sentence:
                for bd in budayu:
                    if bd in sentence:
                        relation = '小于'
                return '大于'
        for d in xiaoyu:
            if d in sentence:
                for bd in buxiaoyu:
                    if bd in sentence:
                        relation = '大于'
                relation = '小于'

    # 地址约束
    for d in weiyu:
        if d in sentence and is_location:
            relation = '位于'

    for d in fou:
        if d in sentence:
            flag = True
            for d11 in buxiaoyu:
                if d in d11 and d11 in sentence:
                    flag = False
            for d12 in budayu:
                if d in d12 and d12 in sentence:
                    flag = False
            if flag:
                relation = '否'

    return relation







