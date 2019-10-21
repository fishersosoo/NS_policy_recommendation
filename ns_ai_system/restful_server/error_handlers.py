# encoding=utf-8
"""定义错误处理"""
from flask import jsonify

from restful_server.server import app


class MissingParam(Exception):
    status_code = 400

    def __init__(self, *params, status_code=None, payload=None):
        Exception.__init__(self)
        self.params = params
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = f"缺失以下参数:{ ', '.join(self.params)}"
        return rv

@app.errorhandler(MissingParam)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response