# coding=utf-8

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_pymongo import PyMongo

from model.bert_vec import tokenization
from read_config import ConfigLoader

config = ConfigLoader()
ns_data_access_jar_path = config.get('data_server', 'jar_path')
app = Flask("data_server", )
app.config["MONGO_URI"] = f"mongodb://{config.get('mongoDB','host')}:{config.get('mongoDB','port')}/ai_system"
mongo = PyMongo(app)
jsonrpc = JSONRPC(app, service_url="/data", enable_web_browsable_api=True)
tokenizer = tokenization.FullTokenizer(
    vocab_file=config.get("data_server", "vocab_file"), do_lower_case=True)
max_seq=int(config.get("data_server", "max_seq"))
from data_server.jvm_proxy import _start_jvm_for_data_access, DataServiceJavaProxy

_start_jvm_for_data_access()
DataServiceJavaProxy.init(config.get("data_server", "uid"), config.get("data_server", "ip"))
from .views import *
