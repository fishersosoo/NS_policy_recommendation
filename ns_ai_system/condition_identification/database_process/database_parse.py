# coding=utf-8
from condition_identification.name_entity_recognition.extract_keyword import *
from condition_identification.util.distance_calculations import cos_sim
from condition_identification.rule.adjust_database_keyword import adjust_database_keyword_byrule
import pandas as pd
import numpy as np
from tqdm import tqdm
from condition_identification.args import database_cluster_quantile
from condition_identification.args import database_cluster_max_length
from condition_identification.args import database_cluster_min_length
from condition_identification.args import database_cluster_similarity
from condition_identification.name_entity_recognition.vectorize.bert_word2vec import BertClient

def data_filter(database_value):
    bert_client = BertClient()
    values_set = set(database_value)
    values_set = database_extract(values_set, bert_client)
    return values_set



def database_extract(database_values, bc, max_length=-1, len_threshold=1):
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
    database_keywords = []
    for index, database_value in enumerate(database_values):
        if max_length != -1 and index > max_length:     # max_length不是-1，抽取前max_length行
            break
        database_keywords.extend(extract_keyword(database_value, len_threshold))
    database_cluster_result = database_cluster(database_keywords, bc)
    return database_cluster_result


def database_cluster(database_keywords, bc):
    """对数据库列数据聚类

    对列数据很多的列进行聚类，从而剔除无关值

    Args:
        database_keywords： list, 对数据库列值抽取关键词之后的数据
        bc: BertClient,bert词向量工具
    Returns:
         cluster_word: list 返回抽取后的列值

     """
    tqdm.pandas()
    # # 获得列数据的词向量 以及 对列数据去重
    database_keyword_vecs = bc.encode(database_keywords)
    # 如果数据太少就没有清除的必要
    database_keywords_len = len(database_keywords)
    if database_keywords_len < database_cluster_min_length:    # 数据过少不做后续处理直接返回
        return database_keywords
    elif database_keywords_len > database_cluster_max_length:
        database_keyword_vecs = database_keyword_vecs[0:database_cluster_max_length]
        database_keywords = database_keywords[0:database_cluster_max_length]
    database_keywords = adjust_database_keyword_byrule(database_keywords)
    # 循环计算相似度
    count_dict = {keyword: 0 for keyword in database_keywords}
    for index, database_keyword in tqdm(enumerate(database_keywords)):
        for i in range(index+1, database_keywords_len):
            if cos_sim(database_keyword_vecs[index], database_keyword_vecs[i]) > database_cluster_similarity:
                count_dict[database_keyword] += 1

    # 取前0.4的数值
    count_dict = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
    count_dict = count_dict[0:int(len(count_dict)*database_cluster_quantile)]
    cluster_word = [x[0] for x in count_dict]
    return cluster_word


if __name__ == '__main__':
    words = ['1']*1000
    with open('F:\\txt\\txt\\2.txt', 'r', encoding='utf8')as rf:
        for line in rf:
            words.append(line.strip())
