# coding=utf-8
from data_server.server import app
from read_config import ConfigLoader

if __name__ == '__main__':
    config = ConfigLoader()
    print(config.get('data_server', 'port'))
    app.run(host="0.0.0.0", debug=False, port=int(config.get('data_server', 'port')), threaded=True)
