# coding=utf-8
# from data_management.config import py_client
from condition_identification.name_entity_recognition.args import *


def list_field_info():
    """获取field值

    获取所有field的信息

    Returns:
        field : list
        example: ["企业基本信息","企业股东及出资信息","企业主要管理人员信息"]
    """


def get_value_dic():
    """获取value_dic

    从数据库获取value_dic

    Returns:
        value_dic: dict    key值是数据库字段名，value 是数据值,是一个list数组的形式
        example:  {"企业基本信息_地址":["广州市南沙区金隆路26号1402房"],"企业基本信息_经营业务范围":["航空项目"]}


    """


if __name__ == '__main__':
    # print(list_field_info())
    print(get_value_dic())
    # try:
    #     raise Exception("1")
    # except Exception as e:
    #     print(e)
