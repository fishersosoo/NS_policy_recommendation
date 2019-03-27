# coding=utf-8

from pyhanlp import *
from condition_identification.name_entity_recognition.util import  cos_sim
import re
import pandas as pd
def filter_punctuation(LEMMA,HEADLEMMA):
    LEMMA = LEMMA.strip()
    HEADLEMMA = HEADLEMMA.strip()
    LEMMA = re.sub(u"[！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。，； ,;]+", "",
                   LEMMA)

    HEADLEMMA = re.sub(u"[！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。，；,; ]+", "",
                       HEADLEMMA)
    return LEMMA,HEADLEMMA

def filter_book(LEMMA):
    LEMMA = LEMMA.strip()
    LEMMA = re.sub(u"[<《＜].*[>》＞]", "",LEMMA)
    return LEMMA
def filter_brackets(LEMMA):
    LEMMA = LEMMA.strip()
    LEMMA = re.sub(u"[(（].*?[）)]", "",LEMMA)
    return LEMMA
# 按ID顺序插入候选数组
def insert(word,wait_word_id,wait_word):
    if len(wait_word) == 0:
        wait_word.append(word.LEMMA)
        wait_word_id.append(word.ID)
    else:
        l = 0
        # 二分查找优化代码
        while l < len(wait_word_id):
            idp = wait_word_id[l]
            if l + 1 < len(wait_word_id):
                ida = wait_word_id[l + 1]
                if word.ID > idp and word.ID < ida:
                    wait_word.insert(l + 1, word.LEMMA)
                    wait_word_id.insert(l + 1, word.ID)
            else:
                if word.ID > idp:
                    wait_word.insert(l + 1, word.LEMMA)
                    wait_word_id.insert(l + 1, word.ID)
            l += 1
    return wait_word_id,wait_word



#TODO 如果定中之间杂夹了定中分不出来
#TODO 拆value的时候，如果用的是list，会有很多重复，而此时是不需要保持顺序的，只有拆政策文本的时候才需要保持顺序
def extract_keyword(sentence, len_threshold):
    lines=sentence.split(';')
    resultword = []
    for line in lines:
        line = filter_book(line)
        line = filter_brackets(line)
        b = HanLP.parseDependency(line)
        a = b.getWordArray()
        wait_word = []
        history_word = []
        wait_word_id = []
        id_last = 0
        for word in a:
            word.LEMMA, word.HEAD.LEMMA = filter_punctuation(word.LEMMA, word.HEAD.LEMMA)
            if word.DEPREL == '定中关系':
                # 隔太远，即使定中关系也不会成一个词
                if abs(word.ID - word.HEAD.ID) >= 5:
                    continue
                wait_word_id, wait_word = insert(word, wait_word_id, wait_word)
                wait_word_id, wait_word = insert(word.HEAD, wait_word_id, wait_word)
                id_last = word.HEAD.ID
            elif word.ID >= id_last:
                complete_word = ('').join(wait_word)
                if complete_word != '':
                    resultword.append(complete_word)
                    history_word.extend(wait_word)
                    wait_word = []
                    wait_word_id = []
            if word.DEPREL != '定中关系' and 'n' in word.POSTAG and len(
                    word.LEMMA) > len_threshold and word.LEMMA not in history_word:
                resultword.append(word.LEMMA)

        # 最后一个词在最后面的时候
        complete_word = ''.join(wait_word)
        if complete_word != '':
            resultword.append(complete_word)
    return resultword





# def extract_byfile(inputfile,outputfile,len_threshold,max_length=-1):
#     count = 0
#     f = open(outputfile, 'w', encoding='utf8')
#     f.close()
#     with open(inputfile, 'r', encoding='utf8')as rf:
#         for line in rf:
#             count+=1
#             if max_length!=-1:
#                 if count>max_length:
#                     break
#             resultword=extract_keyword(line, len_threshold)
#             f = open(outputfile, 'a', encoding='utf8')
#             for w in resultword:
#                 f.write(w)
#                 f.write('\n')
#             f.close()
#
#
#
# def database_cluster(file):
#     from bert_serving.client import BertClient
#     bc = BertClient()
#
#     import pandas as pd
#     import numpy as np
#     from tqdm import tqdm
#     tqdm.pandas()
#     with open(file, 'r', encoding='utf8')as rf:
#         vs = set()
#         vec_dict = {}
#         for line in tqdm(rf):
#             line = line.strip()
#             vec_dict[line] = bc.encode([line])
#             vs.add(line)
#
#         vs = list(vs)
#         result_csv = pd.DataFrame({'filed': np.array(vs), 'count': np.zeros(len(vs))})
#         diff = 0
#         for key in tqdm(vs):
#             value_csv = pd.DataFrame({'filed': np.array(vs), 'value': np.zeros(len(vs))})
#             diff += 1
#             for j in range(diff, len(vs)):
#                 key2 = vs[j]
#                 value_csv.loc[value_csv['filed'] == key2, 'value'] = cos_sim(vec_dict[key], vec_dict[key2])
#             value_csv = value_csv[value_csv['value'] > 0.9]
#             value_csv = value_csv['filed'].values
#
#             for i in range(value_csv.shape[0]):
#                 result_csv.loc[result_csv['filed'] == value_csv[i], 'count'] += 1
#
#         result_csv=result_csv[result_csv['count']>result_csv['count'].quantile(0.4)]
#         result_csv.to_csv('temp.csv',index=False)
#     with open(file, 'w', encoding='utf8')as wf:
#         result_csv=result_csv['filed'].values
#         for i in range(len(result_csv)):
#             wf.write(result_csv[i])
#             wf.write('\n')
if __name__=='__main__':
    # Field是2，value是1
    # extract_byfile('value/2.txt','evalue/企业基本信息_经营业务范围.txt',1,500)
    # extract_byfile('value/1.txt', 'evalue/企业基本信息_地址.txt', 1, 500)
    # extract_byfile('value/3.txt', 'evalue/企业基本信息_行业领域.txt', 1, 500)
    # database_cluster('evalue/企业基本信息_地址.txt')
    result_csv=pd.read_csv('temp.csv')
    with open('evalue/企业基本信息_地址.txt', 'w', encoding='utf8')as wf:
        result_csv=result_csv['filed'].values
        for i in range(len(result_csv)):
            wf.write(result_csv[i])
            wf.write('\n')






