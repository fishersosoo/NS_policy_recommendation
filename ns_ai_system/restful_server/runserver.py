# coding=utf-8
from read_config import ConfigLoader
from restful_server.server import app

if __name__ == "__main__":
    config = ConfigLoader()
    print(int(config.get("restful_server", "port")))
    app.run(host="0.0.0.0", debug=False, port=int(config.get("restful_server", "port")))
