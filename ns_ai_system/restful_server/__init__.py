# coding=utf-8
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('../config.ini')
config = dict()
# for key, value in cfg.items("server"):
#     config[key] = value

config["port"]=8000