# coding=utf-8
from pyhanlp import *
import re
from condition_identification.util.sentence_preprocess import filter_sentence
from condition_identification.util.sentence_preprocess import filter_punctuation
from bisect import bisect_left





def insert(word, wait_word_id, wait_word):
    """" 把word 插入到合适的数组
     按ID顺序插入候选数组

    Args:
        word:待插入的word
        wait_word:list ,候选词组
        wait_word_id:候选词组的id

    Returns:
        两个list数组

    """
    if word.ID in wait_word_id:
        return wait_word_id, wait_word
    # word.ID 和 word.LEMMA 插入到合适的位置
    pos=bisect_left(wait_word_id, word.ID)
    wait_word_id.insert(pos, word.ID)
    wait_word.insert(pos, word.LEMMA)
    return wait_word_id, wait_word


# 如果定中之间杂夹了定中分不出来
def extract_keyword(sentence, len_threshold):
    """抽取句子的关键词

    利用 pyhanlp 分词和词法分析，获取句子的关键词

    Args:
        sentence: str
        len_threshold: int

    Returns:
        list

    """
    lines = sentence.split('；')
    result_word = []
    for line in lines:
        line = filter_sentence(line)
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

if __name__ == '__main__':
    # with open('evalue/企业基本信息_地址.txt', 'w', encoding='utf8')as wf:
    #     result_csv=result_csv['filed'].values
    #     for i in range(len(result_csv)):
    #         wf.write(result_csv[i])
    #         wf.write('\n')
    # text=['广州市南沙区黄阁镇境界大街22-1号地下室','广州市南沙区南沙街裕兴东街103号101铺','4号1023房',
    #       '广州市南沙区品汇街68号102房','广州市南沙区进港大道12号702房','广州市南沙区南沙街江南路22号101商铺',
    #       '广州市南沙区环市北路1号逸涛雅苑会所302室','广州市南沙区成汇街1号成荟广场商务办公B栋西梯1208房',
    #       '广州市南沙区南沙街环市大道中452号一楼','广州市南沙区进港大道12号1211房','广州市南沙区成汇街3号1108房',
    #       '广州市南沙区海滨路171号南沙金融大厦16楼1601室之22','广州市南沙区海滨路171号南沙金融大厦16楼1601之43',
    #       '广州市南沙区成汇街1号1607房','广州市南沙区大岗镇高沙路蓝怡街2号','核居委广场路','358号101房']
    # for i in text:
    #     print(extract_keyword(i, 2))
    from bisect import bisect_left, bisect_right

    keys=[1,2,5,7,9]
    end = bisect_left(keys, 10)
    print(end)





