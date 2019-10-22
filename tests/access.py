# coding=utf-8
from data_management.api.rpc_proxy import rpc_server
from multiprocessing import Process


def func():
    return_data = rpc_server().data.sendRequest("91440101668125196C", f"DR1.DOM")
    print(return_data)


if __name__ == '__main__':
    p = Process(target=func)
    p.start()
    p.join()
