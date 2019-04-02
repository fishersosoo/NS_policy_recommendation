# coding=utf-8
# from data_management.config import py_client
from condition_identification.name_entity_recognition.args import *
import os
from collections import defaultdict

from data_management.config import py_client


def list_field_info():
    """获取field值

    获取所有field的信息

    Returns:
        field : list
        example: ["企业基本信息","企业股东及出资信息","企业主要管理人员信息"]
    """
    return {one["item_name"].strip() for one in py_client.ai_system["field"].find({"type": "item"})}


def save_value_dict_from_files():
    """
    从目录中读取value_dict数据并保存到数据库中

    :return:
    """
    values = get_value_dic_from_files()
    py_client.ai_system["value_dict"].delete_many({})
    for k, v in values.items():
        py_client.ai_system["value_dict"].insert_one({"key": k.split(".")[0], "value": list(v)})


def get_value_dic_from_files(file_path="../../condition_identification/name_entity_recognition"):
    """获取value_dic

    从数据库获取value_dic,这里获取的是经过set_value_cluster的值

    Returns:
        value_dic: dict    key值是数据库字段名，value 是数据值,是一个list数组的形式
        example:  {"企业基本信息_地址":["广州市南沙区金隆路26号1402房"],"企业基本信息_经营业务范围":["航空项目"]}


    """
    values = defaultdict(set)
    value_file_dir = os.path.join(file_path, 'evalue')
    for file in os.listdir(value_file_dir):
        value_set = set()
        # 从文件中读取value值
        with open(os.path.join(value_file_dir, file), encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if line != '':
                    value_set.add(line)
            values[file] = value_set
    return values


def get_value_dic():
    """获取value_dic

    从数据库获取value_dic,这里获取的是经过set_value_cluster的值

    Returns:
        value_dic: dict    key值是数据库字段名，value 是数据值,是一个list数组的形式
        example:  {"企业基本信息_地址":["广州市南沙区金隆路26号1402房"],"企业基本信息_经营业务范围":["航空项目"]}


    """

    values = defaultdict(set)
    for one in py_client.ai_system["value_dict"].find():
        values[one["key"] + '.txt'] = set(one["value"])
    print(__name__)
    return values


def get_num_fields():
    """获得所有列值是数字的field集合

    Returns：
        num_fields:set,所有值为数字的field值集合
        example：["纳税总额","收入总额"]


    """
    return [one["item_name"] for one in py_client.ai_system["field"].find({"type": "item", "item_type": "literal"})]


def get_address_fields():
    """获得所有列值是地址的field集合

    Returns:
        address_fields: set,所有值为地址的field集合
        example: ["企业地址","办公地址"]

    """
    return ["地址"]


if __name__ == '__main__':
    # print(list_field_info())
    print(get_value_dic())
    # try:
    #     raise Exception("1")
    # except Exception as e:
    #     print(e)
