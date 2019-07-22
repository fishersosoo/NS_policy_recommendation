# coding=utf-8
import re

import pika

from read_config import config


def conert_ch2num(ch):
    ch=ch.strip("元")
    ch=ch.replace("万","0000")
    ch = ch.replace("千", "000")
    ch = ch.replace("百", "00")
    ch = ch.replace("十", "0")
    ch = ch.replace("亿", "000000000")
    return float(ch)


def connect_channel():
    credentials = pika.credentials.PlainCredentials(config.get('rabbit_mq', 'user'), config.get('rabbit_mq', 'pwd'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=config.get('rabbit_mq', 'host'), port=int(config.get('rabbit_mq', 'port')), virtual_host="/",
        credentials=credentials))
    channel = connection.channel()
    return channel