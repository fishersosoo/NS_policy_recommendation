# coding=utf-8
from condition_identification.name_entity_recognition.extract_keyword import *
from condition_identification.util.distance_calculations import cos_sim
import pandas as pd
import numpy as np
from tqdm import tqdm
from condition_identification.name_entity_recognition.vectorize.bert_word2vec import bert_word2vec
bc = bert_word2vec


def database_extract(lines, max_length=-1, len_threshold=1):
    """对数据库的列值进行抽取

    数据库的列值进行抽取,

    Args:
        lines: list传过来的数据库的列值
        len_threshold: int 分词的粒度，一般不用修改
        max_length: int 为了节省时间，可以选择只抽前Man_length条

    Returns:
        None
    """
    result_word = []
    count = 0
    for line in lines:
        count += 1
        if max_length != -1 and count > max_length:     # max_length不是-1，抽取前max_length行
            break
        result_word.extend(extract_keyword(line, len_threshold))
    result = database_cluster(result_word)
    return result


def database_cluster(lines):
    """对数据库列数据聚类

    对列数据很多的列进行聚类，从而剔除无关值

    Args:
        lines: list 传过来的数据库的列值

     Returns:
         result: list 返回抽取后的列值

     """
    tqdm.pandas()
    vs = set()
    vec_dict = {}
    result = lines
    # 获得列数据的词向量 以及 对列数据去重
    strs=[]
    for line in tqdm(lines):
        line = line.strip()
        strs.append(line)
    vecs=bc([strs])
    for line,vec in zip(strs,vecs):
        vec_dict[line] =vec
        vs.add(line)
    vs = list(vs)
    # 如果数据太少就没有清除的必要
    if len(vs) > 300:
        # 计算与其他数据的相似度，取相似度最高的那些数据
        result_csv = pd.DataFrame({'field': np.array(vs), 'count': np.zeros(len(vs))})
        diff = 0
        for key in tqdm(vs):
            value_csv = pd.DataFrame({'field': np.array(vs), 'value': np.zeros(len(vs))})
            diff += 1
            # 计算与其他列数据的相似度
            for j in range(diff, len(vs)):
                key2 = vs[j]
                value_csv.loc[value_csv['field'] == key2, 'value'] = cos_sim(vec_dict[key], vec_dict[key2])
            value_csv = value_csv[value_csv['value'] > 0.9]    # 对相似度大于0.9 的count 加一
            value_csv = value_csv['field'].values
            for i in range(value_csv.shape[0]):
                result_csv.loc[result_csv['field'] == value_csv[i], 'count'] += 1
        result_csv = result_csv[result_csv['count'] > result_csv['count'].quantile(0.4)]     # 取count 值最大的前百分之四十
        result = result_csv['field'].values
    return result


if __name__ == '__main__':
    words = ['1']*1000
    with open('F:\\txt\\txt\\2.txt' , 'r',encoding='utf8')as rf:
        for line in rf:
            words.append(line.strip())
