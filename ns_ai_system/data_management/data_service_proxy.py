# coding=utf-8
from flask_jsonrpc.proxy import ServiceProxy


class DataService:
    server = None

    def __init__(self, url="http://127.0.0.1:50000/data"):
        DataService.server = ServiceProxy(service_url=url)

    def sendRequest(self, service_name, params):
        """
        请求数据

        :param service_name: 数据服务名字
        :param params: 查询参数
        :return: 返回数据
        """
        value = DataService.server.data.sendRequest(service_name, params)
        # print(value)
        return value["result"]
