# coding=utf-8
import json

import pika
import pika.exceptions
from celery_task import celery_app, channel
from celery_task.policy.tasks import _check_single_guide
from service import connect_channel


def push_message(routing_key, message):
    global channel
    while True:
        try:
            channel.basic_publish(exchange='task', routing_key=routing_key, body=json.dumps(message))
            return
        except pika.exceptions.ConnectionClosedByBroker:
            channel = connect_channel()
            continue
            # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:
            print("Caught a channel error: {}, stopping...".format(err))
            break
            # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            channel = connect_channel()
            print("Connection was closed, retrying...")
            continue
