# coding=utf-8
import math
import time

import numpy as np
from flask_jsonrpc.proxy import ServiceProxy

from data_management.config import config

vec_cache = dict()


def bert_word2vec(strs):
    strs = list(strs)
    strs_no_cache = []
    for string in strs:
        if string not in vec_cache:
            strs_no_cache.append(string)
    print(f"process {len(strs)} strings")
    if len(strs_no_cache)!=0:
        strs_no_cache_vecs = _bert_word2vec(strs_no_cache)
        for string, vec in zip(strs_no_cache, strs_no_cache_vecs):
            vec_cache[string] = vec
        print(f"cache {len(strs_no_cache_vecs)} vectors")
    rets = []
    for string in strs:
        rets.append(vec_cache[string])
    return rets


def _bert_word2vec(strs):
    """
    使用bert模型进行char level的 word2vec

    :param strs: [str]. 多个str
    :return:
    list, shape:[len(strs), 32, 768]

    """
    # s=time.time()
    rets = []
    strs = list(strs)
    ip = config.get('data_server', 'host')
    # ip = "ns.fishersosoo.xyz"
    url = f"http://{ip}:3306/data"
    batch_size = 200
    batch = math.ceil(len(strs) / batch_size)
    print(f"no cache {len(strs)} strings in {batch} batches")
    last = 0
    for i in range(batch - 1):
        last = (i + 1) * batch_size
        server = ServiceProxy(service_url=url)
        ret = server.model.bert_word2vec(strs[i * batch_size:(i + 1) * batch_size])
        # print(ret.keys)
        ret = ret["result"]
        ret = np.mean(ret, axis=1).tolist()
        rets.extend(ret)
    # print(strs[last:])
    server = ServiceProxy(service_url=url)
    ret = server.model.bert_word2vec(strs[last:])
    # print(ret.keys())
    # print(ret["error"])
    ret = ret["result"]
    ret = np.mean(ret, axis=1).tolist()
    rets.extend(ret)
    # print(time.time()-s)
    # print(time.time()-s)
    assert len(rets) == len(strs)
    return rets


if __name__ == '__main__':
    print((bert_word2vec(["测试一下"] * 90)))
