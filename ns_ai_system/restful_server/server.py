# coding=utf-8

from flask import Flask
from flask_pymongo import PyMongo

from restful_server.func import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.config["MONGO_URI"] = "mongodb://ns.fishersosoo.xyz:80/ai_system"
mongo = PyMongo(app)

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


# @app.before_first_request
# def before_first():
#     DictManagement.reload_dict()


app.register_blueprint(policy_service, url_prefix="/policy/")
