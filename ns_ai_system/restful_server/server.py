# coding=utf-8

from flask import Flask
from flask_pymongo import PyMongo

from read_config import ConfigLoader
from restful_server.func import CustomJSONEncoder

from concurrent.futures.thread import ThreadPoolExecutor
# pool=ThreadPoolExecutor(1)
config = ConfigLoader()
app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.config["MONGO_URI"] = f"mongodb://{config.get('mongoDB','host')}:{config.get('mongoDB','port')}/ai_system"
mongo = PyMongo(app)
from restful_server.policy import policy_service


@app.route("/")
def index():
    return "", 200


app.register_blueprint(policy_service, url_prefix="/policy/")
