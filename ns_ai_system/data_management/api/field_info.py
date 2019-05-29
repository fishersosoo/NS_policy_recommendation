# coding=utf-8
"""
提供查询数据表基本信息的接口
"""
from data_management.config import py_client


def list_all_field_name():
    """
    获取所有field的名称

    Returns:
        field : list
        example: ["企业基本信息","企业股东及出资信息","企业主要管理人员信息"]
    """
    field_info = get_all_field_info()
    return {one["item_name"].strip() for one in field_info}


def get_all_field_info():
    """

    获取所有field的信息

    Returns: example: [{"resource_id":"DR1","resource_name":"企业基本信息","item_id":"ENTNAME","item_name":"企业名称",
    "type":"item","item_type":"name"}, {}, {}]
    """
    return list(py_client.ai_system["field"].find({"type": "item"}))


def get_field_values(item_id):
    """
    获取某个字段的的可能取值

    :param item_id: 字段id. 通过get_all_field_info()函数可以获取
    :return:["value1", "value2", ...]
    """
    results = list(py_client.ai_system["field_value"].find({"item_id": item_id}))
    return [one["value"] for one in results]


def get_num_fields():
    """
    获得所有列值是数字的field集合

    Returns：
        num_fields:set,所有值为数字的field值集合
        example：["纳税总额","收入总额"]


    """
    return ['营业总收入', '纳税总额', '注册资本', '资产总额', '实缴出资额']


def get_address_fields():
    """
    获得所有列值是地址的field集合

    Returns:
        address_fields: set,所有值为地址的field集合
        example: ["企业地址","办公地址"]

    """
    return ["地址"]
