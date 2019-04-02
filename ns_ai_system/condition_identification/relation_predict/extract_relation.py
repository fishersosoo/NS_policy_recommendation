# coding=utf-8
# rule
dayu = ['大于', '以上', '超过', '多于', '高于', '至多', '以后']
budayu = ['不' + x for x in dayu]
xiaoyu = ['小于', '以下', '少于', '低于', '至少', '未满', '以前']
buxiaoyu = ['不' + x for x in xiaoyu]
weiyu = ['位于', '区内', '范围内']
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
    relation = relation_pre(pre_sentence)
    return relation


def relation_pre(sentence):
    """ 关系抽取

    具体根据关键字抽取的逻辑

    Args:
        sentence: 预处理后的句子

    Returns:
        str:返回的具体关系值，判断不出的一律返回"是"
    """
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
    for d in weiyu:
        if d in sentence:
            return '位于'
    for d in fou:
        if d in sentence:
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
