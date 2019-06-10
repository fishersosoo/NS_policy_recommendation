# coding=utf-8

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_pymongo import PyMongo
from zeep import Client

from model.bert_vec import tokenization
from read_config import ConfigLoader
from my_log import Loggers
import logging

url = "http://47.106.70.192/webService/services/ws?wsdl"
uid="F30FD00E373FD16544C308A6BD5CFDE2"
client = Client(url)

config = ConfigLoader()
app = Flask("data_server", )
app.config["MONGO_URI"] = f"mongodb://{config.get('mongoDB','host')}:{config.get('mongoDB','port')}/ai_system"
app.logger.setLevel(logging.DEBUG)
Loggers.init_app('data',app.logger)
mongo = PyMongo(app)
jsonrpc = JSONRPC(app, service_url="/data", enable_web_browsable_api=True)
tokenizer = tokenization.FullTokenizer(
    vocab_file=config.get("data_server", "vocab_file"), do_lower_case=True)
max_seq=int(config.get("data_server", "max_seq"))
from .views import *