# coding=utf-8
"""
数据库访问配置
"""
# from configparser import ConfigParser
#
# cfg = ConfigParser()
# cfg.read('config.ini')

neo4j_config = dict(host="ns.fishersosoo.xyz",
                    user="neo4j",
                    password="1995")
import pymongo

py_client = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80,connect=False)
mongodb = py_client.ai_system
import socket

if socket.gethostname() == "iZwz947of4lcxjw3c833lzZ":
    # 测试服务器环境
    ns_data_access_jar_path = "/home/web/NS_policy_recommendation/ns_ai_system/res/lib/ns_data_access.jar"
else:
    # 本机开发环境
    ns_data_access_jar_path = r"Y:\Nansha AI Services\condition_identification\ns_ai_system\res\lib\ns_data_access.jar"
from data_management.external_data_access import DataService

dataService = DataService()
