# coding=utf-8
# from data_management.config import py_client
from condition_identification.name_entity_recognition.args import *
from condition_identification.database_process.database_parse import database_extract
import os
from collections import defaultdict

FILE_PATH = "../../condition_identification/name_entity_recognition"


def list_field_info():
    """获取field值

    获取所有field的信息

    Returns:
        field : list
        example: ["企业基本信息","企业股东及出资信息","企业主要管理人员信息"]
    """
    # return list(py_client.ai_system["field"].find())
    field = set()
    field_file = os.path.join(FILE_PATH, 'field.txt')
    with open(field_file, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if line != '':
                field.add(line)
    return field


def set_value_cluster(datas):
    """存储聚类后的数据

    对数据库内的句子和词同样作一次关键词抽取,然后剔除无关的词，需要把结果重新存回数据库

    Args:
        datas:list 某一列的值

    Returns:
        None
    """
    wait_for_store=database_extract(datas)





def get_value_dic():
    """获取value_dic

    从数据库获取value_dic,这里获取的是经过set_value_cluster的值

    Returns:
        value_dic: dict    key值是数据库字段名，value 是数据值,是一个list数组的形式
        example:  {"企业基本信息_地址":["广州市南沙区金隆路26号1402房"],"企业基本信息_经营业务范围":["航空项目"]}


    """
    values = defaultdict(set)
    value_file_dir = os.path.join(FILE_PATH, 'evalue')
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


def get_num_fields():
    """获得所有列值是数字的field集合

    Returns：
        num_fields:set,所有值为数字的field值集合
        example：["纳税总额","收入总额"]


    """
    return ["纳税总额", "收入总额"]


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
