from pyhanlp import *

def idf_nums(word):
    """判断是否是数字
    通过分词工具词性分析，判断数字
    Args:
        word:str
    Returns:
        True 或者 False
    """
    # 通过词法分析 根据词性判断
    mflag = False
    qflag = False
    for term in HanLP.segment(word):
        nature = str(term.nature)
        word = term.word
        if nature == 'm':
            mflag = True
        if (nature == 'q' or nature == 'l') and (word != '项' and word != '条'):
            print(word)
            qflag = True
    if mflag and qflag:
        return True
    else:
        return False

# 数据库字段的地址就用地的相似度去找，

def idf_address(sentence):
    """判断是否是地址
    判断是否是地址值，利用HanLP的地址识别
    Args:
        sentence:str
    Returns：
        True 或者 False
    """
    # 利用HanLP 接口识别是否是地址值
    segment = HanLP.newSegment().enablePlaceRecognize(False)
    term_list = segment.seg(sentence)
    is_address=False
    for i in term_list:
        nature = str(i.nature)
        word = str(i.word)
        if 'ns' in nature and word != '中国':
            is_address=True
            break
    return is_address

def extract_address(keywords):
    """ 在keyword中提取国家的词语

    :param keywords:
    :return:
    """
    for i in range(len(keywords)):
        sentence=keywords[i]
        segment = HanLP.newSegment().enablePlaceRecognize(False)
        term_list = segment.seg(sentence)
        address_word = [str(i.word) for i in term_list if str(i.nature) == 'ns' and str(i.word) != '中国']
        address_word = ''.join(address_word)
        if address_word:
            keywords[i]=address_word
        else:
            keywords[i]=sentence
    return  keywords