# coding=utf-8
import math
import time
from _socket import timeout

import numpy as np
from flask_jsonrpc.proxy import ServiceProxy
from urllib.request import HTTPError

from data_management.config import redis_cache
from bert_serving.client import BertClient as _BertClient


def _check_NONE(vectors):
    for v in vectors:
        assert v is not None


def _from_cache(strs):
    """
    从redis缓存中查找向量化的结果

    :param strs:
    :return: vectors, need_compute_strs, need_compute_index.
        vectors 向量化结果，可能会有 None.
        need_compute_strs 需要计算的字符串数组.
        need_compute_index 记录没缓存的字符串下标，用于计算之后填充 vectors 中的 None.
    """
    vectors = redis_cache.mget(strs)
    need_compute_strs = []
    need_compute_index = []
    for index, vector in enumerate(vectors):
        if vector is None:
            need_compute_strs.append(strs[index])
            need_compute_index.append(index)
    print(f"miss {len(need_compute_strs)} in {len(strs)}")
    return vectors, need_compute_strs, need_compute_index


def bert_word2vec(strs, batch_size=200, reduce_mean=True):
    """
    使用bert模型进行char level的 word2vec

    :param strs: [str]. 多个str
    :return:
    list, shape:[len(strs), 32, 768]

    """
    if isinstance(strs, str):
        strs = [strs]
    vectors, need_compute_strs, need_compute_index = _from_cache(strs)
    if len(need_compute_strs) != 0:
        bc = _BertClient()
        compute_vectors = bc.encode(need_compute_strs).tolist()
        for i, compute_vector in enumerate(compute_vectors):
            vectors[need_compute_index[i]] = compute_vector
            redis_cache.set(need_compute_strs[i],compute_vector)
    # _check_NONE(vectors)
    return vectors


class BertClient(object):
    """封装 bert_word2vec

    方便本地测试和修改，本地测试可以用bert_serving

    """

    def encode(self, strs):
        return bert_word2vec(strs)


if __name__ == '__main__':
    print((bert_word2vec(["测试"]*2)))
