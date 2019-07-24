# coding=utf-8
import json

import pika
import pika.exceptions
from read_config import config
import atexit


def clear_up(channel, connection):
    try:
        channel.stop_consuming()
        channel.close()
        connection.close()
    except:
        pass


def connect_channel(connection=None, channel=None):
    """
    获取connection和channel

    Args:
        connection:
        channel:

    Returns:

    """
    if connection is not None or channel is not None:
        clear_up(channel=channel, connection=connection)
        try:
            atexit.unregister(clear_up)
        except:
            pass
    credentials = pika.credentials.PlainCredentials(config.get('rabbit_mq', 'user'), config.get('rabbit_mq', 'pwd'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=config.get('rabbit_mq', 'host'), port=int(config.get('rabbit_mq', 'port')), virtual_host="/",
        credentials=credentials))
    channel = connection.channel()
    atexit.register(clear_up, channel, connection)
    return connection,channel
