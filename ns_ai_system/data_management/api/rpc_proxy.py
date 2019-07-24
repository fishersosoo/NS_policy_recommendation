# coding=utf-8
from flask_jsonrpc.proxy import ServiceProxy

from read_config import config

rpc_server = ServiceProxy(
    service_url=f"http://{ config.get('data_server', 'host')}:{config.get('data_server','port')}/data")
