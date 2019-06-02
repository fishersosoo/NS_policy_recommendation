# coding=utf-8

from flask import Flask
from flask_pymongo import PyMongo

from read_config import ConfigLoader

config = ConfigLoader()

from restful_server.func import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.config["MONGO_URI"] = f"mongodb://{config.get('mongoDB','host')}:{config.get('mongoDB','port')}/ai_system"
mongo = PyMongo(app)
from restful_server.policy import policy_service
from restful_server.init_setup import init_mq

init_mq()


@app.route("/")
def index():
    print(11111)
    return "1111", 200


app.register_blueprint(policy_service, url_prefix="/policy/")
