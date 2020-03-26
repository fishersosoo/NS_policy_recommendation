# coding=utf-8
from condition_identification.util.distance_calculations import cos_sim
from condition_identification.rule.adjust_database_keyword import adjust_database_keyword_byrule
import pandas as pd
import numpy as np

from condition_identification.args import database_cluster_quantile
from condition_identification.args import database_cluster_max_length
from condition_identification.args import database_cluster_min_length
from condition_identification.args import database_cluster_similarity
from condition_identification.name_entity_recognition.vectorize.bert_word2vec import BertClient
from condition_identification.util.sentence_preprocess import filter_punctuation_include_content
from collections import defaultdict


def database_extract(database_values):
    """对数据库的列值进行抽取

    数据库的列值进行抽取,

    Args:
        database_values: list,传过来的数据库的列值
        len_threshold: int 分词的粒度，一般不用修改
        max_length: int 为了节省时间，可以选择只抽前Man_length条
        bc: BertClient,bert词向量工具
    Returns:
        database_cluster_result: list ,聚合处理后的数据库的值
    """

    database_keywords = set()
    for index, database_value in enumerate(database_values):
        if len(database_keywords) > database_cluster_max_length:
            break
        database_keywords = database_keywords.union(set(extract_databaseword(database_value)))

    if len(database_keywords)< database_cluster_min_length:
        database_cluster_result = list(database_keywords)
    else:
        database_cluster_result = database_cluster(database_keywords)
    return database_cluster_result


def extract_databaseword(database_value):
    database_value = filter_punctuation_include_content(database_value)
    database_value.replace('，', ";")
    database_value = database_value.split(';')
    database_value = list(filter(None,database_value))
    return database_value


def database_cluster(database_keywords):
    """对数据库列数据聚类

    对列数据很多的列进行聚类，从而剔除无关值

    Args:
        database_keywords： list, 对数据库列值抽取关键词之后的数据
        bc: BertClient,bert词向量工具
    Returns:
         cluster_word: list 返回抽取后的列值

     """
    bert_client = BertClient()

    database_keywords = adjust_database_keyword_byrule(database_keywords)
    database_keyword_vecs = bert_client.encode(database_keywords)
    # 循环计算相似度
    count_dict = defaultdict(int)
    for index, database_keyword in enumerate(database_keywords):
        vec2s = np.array(database_keyword_vecs[index+1:])
        if len(vec2s)==0:
            break
        vec1 = np.array(database_keyword_vecs[index])
        count_dict[database_keyword]=np.sum(np.apply_along_axis(cos_sim, 1, vec2s, vec1) > database_cluster_similarity)


    # 取前0.4的数值
    count_dict = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
    count_dict = count_dict[0:int(len(count_dict)*database_cluster_quantile)]
    cluster_word = [x[0] for x in count_dict]
    return cluster_word


if __name__ == '__main__':
    a = [[1,2],[2,3],[4,5]]
    b = [3,4]
    a = np.array(a)
    b = np.array(b)
    print(a[3:])
    print(np.apply_along_axis(cos_sim, 1, a,b)>0.5)
    print(np.sum(np.apply_along_axis(cos_sim, 1, a,b)>0.5))



