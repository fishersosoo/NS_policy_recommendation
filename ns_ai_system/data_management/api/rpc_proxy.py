# coding=utf-8
from flask_jsonrpc.proxy import ServiceProxy

from read_config import config

def rpc_server():
    return ServiceProxy(
    service_url=f"http://{ config.get('data_server', 'host')}:{config.get('data_server','port')}/data")
