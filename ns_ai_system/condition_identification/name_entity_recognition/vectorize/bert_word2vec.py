# coding=utf-8
import math
import time
from _socket import timeout

import numpy as np
from flask_jsonrpc.proxy import ServiceProxy
from urllib.request import HTTPError

from data_management.config import config


def bert_word2vec(strs, batch_size=200, reduce_mean=True):
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
    url = f"http://{ip}:3306/data"
    batch = math.ceil(len(strs) / batch_size)
    last = 0
    for i in range(batch - 1):
        last = (i + 1) * batch_size
        server = ServiceProxy(service_url=url)
        try:
            ret = server.model.bert_word2vec(strs[i * batch_size:(i + 1) * batch_size])
            ret = ret["result"]
        except HTTPError as e:
            if e.code == "504":
                print(f"timeout. reduce batch_size to {int(batch_size / 2)}")
                ret = bert_word2vec(strs[i * batch_size:(i + 1) * batch_size], int(batch_size / 2), reduce_mean=False)
            else:
                raise e
        rets.extend(ret)
    server = ServiceProxy(service_url=url)
    try:
        ret = server.model.bert_word2vec(strs[last:])
        ret = ret["result"]
    except HTTPError as e:
        if e.code == "504":
            print(f"timeout. reduce batch_size to {int(batch_size / 2)}")
            ret = bert_word2vec(strs[last:], int(batch_size / 2), reduce_mean=False)
        else:
            raise e
    rets.extend(ret)
    # assert len(rets) == len(strs)
    return rets


class BertClient(object):
    """封装 bert_word2vec

    方便本地测试和修改，本地测试可以用bert_serving

    """

    def encode(self, strs):
        return bert_word2vec(strs)


if __name__ == '__main__':
    print((bert_word2vec(["测试一下"] * 90)))
