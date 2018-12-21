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

mongodb = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80).ai_system
ns_data_access_jar_path = "/home/web/NS_policy_recommendation/ns_ai_system/res/lib/ns_data_access.jar"
from data_management.external_data_access import DataService

dataService = DataService(uid="43733da4883d40678dce02d80e13316a", host="121.52.214.35")
