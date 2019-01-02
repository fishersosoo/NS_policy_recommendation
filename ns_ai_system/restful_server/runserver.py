# coding=utf-8
from restful_server import config
from restful_server.server import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=config["port"], threaded=True)
