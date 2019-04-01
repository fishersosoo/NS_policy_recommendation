# coding=utf-8
from flask_jsonrpc.proxy import ServiceProxy


def bert_word2vec(strs):
    """
    使用bert模型进行char level的 word2vec

    :param strs: [str]. 多个str
    :return:
    list, shape:[len(strs), 32, 768]

    """
    # coding=utf-8
    url = "http://120.77.182.188:3306/data"
    server = ServiceProxy(service_url=url)
    return server.model.bert_word2vec(strs)
