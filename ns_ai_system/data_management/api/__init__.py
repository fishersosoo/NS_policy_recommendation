# coding=utf-8
from data_management.config import py_client


def list_field_info():
    """
    获取所有field的信息

    :return:
    """
    return list(py_client.ai_system["field"].find())


if __name__ == '__main__':
    # print(list_field_info())
    try:
        raise Exception("1")
    except Exception as e:
        print(e)