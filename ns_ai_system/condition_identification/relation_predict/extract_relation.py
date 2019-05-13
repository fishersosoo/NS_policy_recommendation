# coding=utf-8
import re
from condition_identification.util.specialcondition_identify import idf_address,idf_nums
from condition_identification.args import dayu, budayu, xiaoyu, buxiaoyu, fou, weiyu


def get_relation(sentence, word):
    """抽取条件

    根据关键字来判断条件

    Args:
        sentence: str 原句子
        word: str 实体词

    Returns:
        relation: str 关系
    """
    # pre_sentence = preprocess(sentence, word)
    relation = relation_pre(sentence, word)
    return relation, sentence


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
    relation = '是'
    # 数字约束
    if is_num:
        for d in dayu:
            if d in sentence:
                for bd in budayu:
                    if bd in sentence:
                        return '小于'
                    else:
                        relation = '大于'
        for d in xiaoyu:
            if d in sentence:
                for bd in buxiaoyu:
                    if bd in sentence:
                        return '大于'
                    else:
                        relation = '小于'

    # 地址约束
    elif is_location:
        for d in weiyu:
            if d in sentence:
                relation = '位于'
        # 地址只有一个关系
        relation = '位于'

    else:
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


if __name__ == '__main__':
    print(relation_pre('纳税总额在300万元以上', '300万元'))