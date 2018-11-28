# coding=utf-8
"""
数据库访问配置
"""
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('../config.ini')

neo4j_config = dict(host=cfg.get("neo4j", "host"),
                    user=cfg.get("neo4j", "user"),
                    password=cfg.get("neo4j", "password"))
