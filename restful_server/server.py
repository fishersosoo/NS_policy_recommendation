# coding=utf-8
from flask import Flask
import os
from dict_management.dict_manage import DictManagement

app = Flask(__name__)

from restful_server.policy import policy_service


@app.route("/")
def index():
    return "", 200


@app.before_first_request
def before_first():
    DictManagement.reload_dict()


app.register_blueprint(policy_service, url_prefix="/policy/")
