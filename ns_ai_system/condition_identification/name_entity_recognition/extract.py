# coding=utf-8
from pyhanlp import *
import pyhanlp
import re


def filter_punctuation(lemma, head_lemma):
    """过滤奇怪的标点符号

    把句子中的标点符号，以及一些奇怪的字符全部去掉

    Args:
        lemma：str
        head_lemma: str

    Returns:
         处理后两个新的字符串

    """
    lemma = lemma.strip()
    head_lemma = head_lemma.strip()
    # 正则表达式操作把标点符号去掉，换成空字符
    lemma = re.sub(u"[！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》"
                   u"「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。 ,;]+", "",
                   lemma)

    head_lemma = re.sub(u"[！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》"
                        u"「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。,; ]+", "", head_lemma)
    return lemma, head_lemma


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
    # word.ID 和 word.LEMMA 插入到合适的位置
    if len(wait_word) == 0:     # 候选数组为空，直接插入
        wait_word.append(word.LEMMA)
        wait_word_id.append(word.ID)
    elif word.ID > wait_word_id[len(wait_word_id)-1]:    # word.ID 大于wait_word_id 最后一个
        wait_word_id.append(word.ID)                     # 直接放到最后面
        wait_word.append(word.LEMMA)
    else:
        for i in range(len(wait_word_id)):
            if word.ID < wait_word_id[i]:
                wait_word_id.insert(i, word.ID)
                wait_word.insert(i, word.LEMMA)
                break

    return wait_word_id, wait_word


# TODO 如果定中之间杂夹了定中分不出来
# TODO 拆value的时候，如果用的是list，会有很多重复，而此时是不需要保持顺序的，只有拆政策文本的时候才需要保持顺序
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
        line = filter_book(line)
        line = filter_brackets(line)
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
                complete_word = ('').join(wait_word)
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

if __name__=='__main__':
    # with open('evalue/企业基本信息_地址.txt', 'w', encoding='utf8')as wf:
    #     result_csv=result_csv['filed'].values
    #     for i in range(len(result_csv)):
    #         wf.write(result_csv[i])
    #         wf.write('\n')
    print(extract_keyword('1、工商注册地、税务征管关系及统计关系在广州市南沙区范围内；', 2))





