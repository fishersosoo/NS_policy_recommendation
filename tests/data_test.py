# coding=utf-8
import json

from zeep import Client

from data_management.config import mongodb

if __name__ == '__main__':
    # ip = "121.52.214.35"
    url = "http://47.106.70.192/webService/services/ws?wsdl"

    client = Client(url)
    value = client.service.getParamInfo("F30FD00E373FD16544C308A6BD5CFDE2", "91440101717852200L",
                                        "DR1.REGCAP")._value_1
    value = json.loads(value)
    if value["Status"] == "Success":
        result = value["Result"]
        print(result)
    # print()
