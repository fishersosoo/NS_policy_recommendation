# coding=utf-8
import json

from celery import Celery
from flask import Flask, request

# from restful_server.celery_ import celery
from condition_identification.dict_management.dict_manage import DictManagement

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://ns.fishersosoo.xyz:8000',
    CELERY_RESULT_BACKEND='redis://ns.fishersosoo.xyz:8000',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
)


from restful_server.policy import policy_service


@app.route("/")
def index():
    return "", 200


# @celery.task
# def do_add(a, b):
#     return a + b


# @app.route("/add",methods=["POST"])
# def test_celery():
#     kwargs = json.loads(request.data)
#     result=do_add.delay(kwargs["a"], kwargs["b"])
#     print(result)
#     return "", 200


@app.before_first_request
def before_first():
    DictManagement.reload_dict()


app.register_blueprint(policy_service, url_prefix="/policy/")
