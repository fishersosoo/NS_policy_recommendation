# coding=utf-8
from data_server.server import app
from read_config import config
from service.rabbitmq import init_mq
from service.rabbitmq.comsumer import create_consum_process

if __name__ == '__main__':
    print(config.get('data_server', 'port'))
    init_mq()
    create_consum_process()
    app.run(host="0.0.0.0", debug=False, port=int(config.get('data_server', 'port')), threaded=False)
