# coding=utf-8
from restful_server.server import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
    # app.run(host="0.0.0.0", port=8000)
