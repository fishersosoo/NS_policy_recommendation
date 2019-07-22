# coding=utf-8
from read_config import config
from restful_server.server import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=int(config.get("restful_server", "port")))
