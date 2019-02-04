# coding=utf-8

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/callback/", methods=["POST"])
def callback_func():
    params = request.json
    print(params)
    if params["task_id"] == "test":
        return jsonify(params["result"]["test"]["matching"])
    return jsonify(None)


if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=False, port=8002)
