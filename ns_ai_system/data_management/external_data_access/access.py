# coding=utf-8
from data_management.config import dataService

if __name__ == '__main__':
    params = dict()
    params.__setitem__("keyword", "广州威万事家居股份有限公司")
    params.__setitem__("type", 0)
    value = dataService.sendRequest("getEntByKeyword", params)
    print(value)
