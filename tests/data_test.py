# coding=utf-8
from zeep import Client

if __name__ == '__main__':
    # ip = "121.52.214.35"
    url = "http://47.106.70.192/webService/services/ws?wsdl"

    client = Client(url)
    print(client.service.getParamInfo("F30FD00E373FD16544C308A6BD5CFDE2", "91440101717852200L","DR1.INDUSTRYCO")._value_1)

