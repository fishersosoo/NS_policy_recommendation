# coding=utf-8
import time

import numpy as np
from flask_jsonrpc.proxy import ServiceProxy

from data_management.config import config


def bert_word2vec(strs):
    """
    使用bert模型进行char level的 word2vec

    :param strs: [str]. 多个str
    :return:
    list, shape:[len(strs), 32, 768]

    """
    # s=time.time()
    strs=list(strs)
    ip = config.get('data_server', 'host')
    url = f"http://{ip}:3306/data"
    server = ServiceProxy(service_url=url)
    ret=server.model.bert_word2vec(strs)["result"]
    # print(time.time()-s)
    ret= np.mean(ret,axis=1)
    # print(time.time()-s)
    return ret


class BertClient(object):
    """封装 bert_word2vec

    方便本地测试和修改，本地测试可以用bert_serving

    """
    def encode(self,strs):
        return bert_word2vec(strs)


if __name__ == '__main__':
    print((bert_word2vec(["测试一下"]*90)))
