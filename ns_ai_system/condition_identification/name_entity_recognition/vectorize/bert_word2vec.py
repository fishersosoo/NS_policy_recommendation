# coding=utf-8
import math
import time
from _socket import timeout

import numpy as np
from flask_jsonrpc.proxy import ServiceProxy
from urllib.request import HTTPError

from data_management.config import config
from bert_serving.client import BertClient as _BertClient

def bert_word2vec(strs, batch_size=200, reduce_mean=True):
    """
    使用bert模型进行char level的 word2vec

    :param strs: [str]. 多个str
    :return:
    list, shape:[len(strs), 32, 768]

    """
    bc=_BertClient()
    if isinstance(strs,str):
        strs=[strs]
    start_time = time.time()
    return bc.encode(strs).tolist()



class BertClient(object):
    """封装 bert_word2vec

    方便本地测试和修改，本地测试可以用bert_serving

    """

    def encode(self, strs):
        return bert_word2vec(strs)


if __name__ == '__main__':
    print((bert_word2vec(["测试一下"] * 2)))
