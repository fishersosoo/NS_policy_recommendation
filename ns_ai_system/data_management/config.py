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
