# coding=utf-8
import pika
from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_pymongo import PyMongo
from zeep import Client
from zeep.transports import Transport

from model.bert_vec import tokenization
from read_config import config
from my_log import Loggers
import logging

from service.rabbitmq.rabbit_mq import connect_channel

url = f"http://{ config.get('data_server','ip') }/webService/services/ws?wsdl"
uid = f"{config.get('data_server','uid')}"
transport = Transport(operation_timeout=3)
client = Client(url, transport=transport)

app = Flask("data_server", )
app.config["MONGO_URI"] = f"mongodb://{config.get('mongoDB','host')}:{config.get('mongoDB','port')}/ai_system"
app.logger.setLevel(logging.DEBUG)
Loggers.init_app('data', app.logger)
mongo = PyMongo(app)
jsonrpc = JSONRPC(app, service_url="/data", enable_web_browsable_api=True)
tokenizer = tokenization.FullTokenizer(
    vocab_file=config.get("data_server", "vocab_file"), do_lower_case=True)
max_seq = int(config.get("data_server", "max_seq"))
connection, channel = connect_channel()


from .views import *
