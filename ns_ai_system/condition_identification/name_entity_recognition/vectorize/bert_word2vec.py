# coding=utf-8
from flask_jsonrpc.proxy import ServiceProxy

from data_management.config import config


def bert_word2vec(strs):
    """
    使用bert模型进行char level的 word2vec

    :param strs: [str]. 多个str
    :return:
    list, shape:[len(strs), 32, 768]

    """
    ip = config.get('data_server', 'host')
    url = f"http://{ip}:3306/data"
    server = ServiceProxy(service_url=url)
    return server.model.bert_word2vec(strs)["result"]


if __name__ == '__main__':
    print(bert_word2vec(["测试一下", "测试"]))
