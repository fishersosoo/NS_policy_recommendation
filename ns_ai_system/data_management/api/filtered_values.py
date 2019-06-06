# coding=utf-8
"""
提供数据列的过滤后的值进行增删改查等操作的接口
"""
from data_management.config import py_client
from data_management.api.field_info import get_all_field_info
from condition_identification.args import FILTED_FIELD
def insert_filtered_values(*filtered_values):
    """
    保存每个数据列过滤后的值。重复的key不会覆盖。

    Examples:
    insert_filtered_values(
        {'field': 'field_1', 'values': [1, 2, 3, 4, 5]},
        {'field': 'field_2', 'values': [1, 2, 3, 4, 5]}
    )
    Args:
        *filtered_values: 形如 {'field': 'field_1', 'values': [1, 2, 3, 4, 5]} 的字典

    Returns:
        None
    """
    py_client.ai_system["field_filtered_values"].insert_namy(filtered_values)


def update_filtered_values(field, new_values):
    """
    更新某个数据列过滤后的值。如果没有则创建

    Examples:
        update_filtered_values("field_1",[8,9,0])

    Args:
        field: 数据列列名
        new_values: list. 新的数据值

    Returns:

    """
    py_client.ai_system["field_filtered_values"].update_one({"field": field}, {"$set":{"values": new_values}}, upsert=True)


def delete_filtered_values(field):
    """
    删除某个数据列过滤后的值

    Examples:
            delete_filtered_values("field_1")

    Args:
        field: 数据列列名

    Returns:
        None
    """
    py_client.ai_system["field_filtered_values"].delete_one({"field": field})


def get_filtered_values(field):
    """
    获取某个数据列过滤后的值

    Examples:
            get_filtered_values("field_1")

    Args:
        field: 数据列列名

    Returns:
        如果没有则返回None

        Examples:
            {'field': 'field_1', 'values': [1, 2, 3, 4, 5]}

    """
    return py_client.ai_system["field_filtered_values"].find_one({"field": field})

def clean_up_filtered_values():
    """
    清空所有field对应的值

    """
    all_field_info = get_all_field_info()
    for field_info in all_field_info:
        item_name = field_info['item_name']
        delete_filtered_values(item_name)
    update_filtered_values(FILTED_FIELD,[])
    return True
if __name__ =='__main__':
    clean_up_filtered_values()