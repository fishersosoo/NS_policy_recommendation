# coding=utf-8
import re
from condition_identification.name_entity_recognition.value import Value
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
    is_num = Value.idf_nums(word)
    is_location = Value.idf_address(word)
    # 数字约束
    if is_num:
        for d in dayu:
            if d in sentence:
                for bd in budayu:
                    if bd in sentence:
                        return '小于'
                return '大于'
        for d in xiaoyu:
            if d in sentence:
                for bd in buxiaoyu:
                    if bd in sentence:
                        return '大于'
                return '小于'

    # if not Value.idf_nums(sentence):
    #     for d in dayu:
    #         if d in sentence:
    #             for bd in budayu:
    #                 if bd in sentence:
    #                     return '小于'
    #             return '大于'
    #     for d in xiaoyu:
    #         if d in sentence:
    #             for bd in buxiaoyu:
    #                 if bd in sentence:
    #                     return '大于'
    #             return '小于'

    # 地址约束
    if is_location:
        return "位于"

    for d in weiyu:
        if d in sentence and Value.idf_address(word):
            return '位于'

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
                return '否'

    return '是'


def preprocess(sentence, word):
    """预处理

    根据，。；对句子进行一个分割，找出实体所在的那个句子段，这样可以避免多个关系在同一个长句子中

    Args:
        sentence: str 原句子
        word: str 实体

    Returns:
        max_s: str 最有可能实体所在的句子
    """

    sentence = filter_sentence(sentence)
    candicate_sentence = []  # 候选的句子段
    for l1 in sentence.split('。'):
        for l2 in l1.split('；'):
            for l3 in l2.split('，'):
                candicate_sentence.append(l3)
    sim_max = 0
    sim_max_s = ''
    # 判断的逻辑为与实体字相同最多的句子为所在句子。相同多的情况下取最后一个
    for s1 in candicate_sentence:
        count = 0
        for w in word:
            if w in s1:
                count += 1
        if count > sim_max:
            sim_max = count
            sim_max_s = s1
    return sim_max_s

#TODO 有待和实体抽取的整合
def filter_sentence(sentence):
    """过滤句子的无关内容

    实际上是调用各个过滤函数的主体函数

    """

    sentence = filter_book(sentence)
    sentence = filter_brackets(sentence)
    return sentence


def filter_book(lemma):
    """过滤掉尖括号和尖括号之间的字符

    把字符串中的尖括号跟括号里的所有字符去掉

    Args:
        lemma:str

    Returns:
        处理后新的字符串

    """
    lemma = lemma.strip()
    lemma = re.sub(u"[<《＜].*[>》＞]", "", lemma)
    return lemma


def filter_brackets(lemma):
    """过滤掉小括号和小括号之间的字符

    把字符串中的小括号及括号里的所有字符去掉

    Args:
        lemma：str，要处理的字符串

    Returns:
        处理后的字符串

    """
    lemma = lemma.strip()
    lemma = re.sub(u"[(（].*?[）)]", "", lemma)
    return lemma