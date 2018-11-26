# coding=utf-8
from flask import Flask

app = Flask(__name__)

from restful_server.policy import policy_service


@app.route("/")
def index():
    return "", 200


app.register_blueprint(policy_service, url_prefix="/policy/")
