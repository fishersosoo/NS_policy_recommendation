# coding=utf-8

import re
from condition_identification.util.sentence_preprocess import filter_punctuation
from bisect import bisect_left


def insert(word, wait_word_id, wait_word):
    """" 把word 根据id插入到合适的位置

    抽取关键词，不能改变关键词组里词的位置顺序，
    因此将词按照id大小插入合适的位置，
    用二分法找到插入位置。

    Args:
        word: str ，待插入的词
        wait_word:list ,候选词组成的list，有定中关系的词
        wait_word_id:候选词组的id

    Returns:
        wait_word_id: list,
        wait_word: list，有定中关系的词
            Examples: wait_word: ['广州市', '南沙区', '范围', '内']

    """
    if word.ID in wait_word_id:
        return wait_word_id, wait_word
    # word.ID 和 word.LEMMA 插入到合适的位置
    pos = bisect_left(wait_word_id, word.ID)
    wait_word_id.insert(pos, word.ID)
    wait_word.insert(pos, word.LEMMA)
    return wait_word_id, wait_word


# 如果定中之间杂夹了定中分不出来
def extract_keyword(sentence, len_threshold):
    """抽取政策条件语句的关键词

       利用 pyhanlp 对政策语句进行分词和词法分析，获取关键词

       Args:
           sentence: str
               Examples: '工商注册地、税务征管关系及统计关系在广州市南沙区范围内；'
           len_threshold: int,

       Returns:
           result_word: list,政策语句的关键词
               Examples:  ['工商注册地', '征管关系', '统计关系', '广州市南沙区范围内']

       """
    from pyhanlp import HanLP
    lines = sentence.split('；')
    result_word = []
    for line in lines:
        b = HanLP.parseDependency(line)
        word_array = b.getWordArray()
        wait_word = []
        history_word = []
        wait_word_id = []
        id_last = 0
        # 词法分析，利用定中关系对分词的结果进一步提取出关键词
        for word in word_array:
            word.LEMMA, word.HEAD.LEMMA = filter_punctuation(word.LEMMA, word.HEAD.LEMMA)
            if word.DEPREL == '定中关系':
                if abs(word.ID - word.HEAD.ID) >= 5:   # 隔太远，即使定中关系也不会成一个词
                    continue
                wait_word_id, wait_word = insert(word, wait_word_id, wait_word)
                wait_word_id, wait_word = insert(word.HEAD, wait_word_id, wait_word)
                id_last = word.HEAD.ID    # 与定中关系有关的id最大的词的下标
            elif word.ID >= id_last:      # word.ID 大于等于有定中关系的词的最大的下标就把之前的词连起来
                complete_word = ''.join(wait_word)
                if complete_word != '':
                    result_word.append(complete_word)
                    history_word.extend(wait_word)
                    wait_word = []
                    wait_word_id = []
            if word.DEPREL != '定中关系' and 'n' in word.POSTAG and len(    # 把大于阈值并且不在历史词里的名词加进去
                    word.LEMMA) > len_threshold and word.LEMMA not in history_word:
                result_word.append(word.LEMMA)
        complete_word = ''.join(wait_word)    # 最后一个词在最后面的时候
        if complete_word != '':
            result_word.append(complete_word)
    return result_word







