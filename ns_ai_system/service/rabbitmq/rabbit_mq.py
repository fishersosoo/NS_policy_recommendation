# coding=utf-8
import pika

from read_config import config


def get_mq_channel():
    credentials = pika.credentials.PlainCredentials(config.get('rabbit_mq', 'user'), config.get('rabbit_mq', 'pwd'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=config.get('rabbit_mq', 'host'), port=int(config.get('rabbit_mq', 'port')), virtual_host="/",
        credentials=credentials))
    channel = connection.channel()
    return channel


def file_event(message, routing_key):
    get_mq_channel().basic_publish(exchange='event.file', routing_key=routing_key, body=message)
