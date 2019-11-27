from data_management.config import py_client
from data_management.api.field_info import get_all_field_info
from condition_identification.args import FILTED_FIELD
def insert_industry_standard(filtered_values):
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
    py_client.ai_system["industry_standard"].insert_one(filtered_values)

def delete_industry_standard(label):
    """
    删除某个数据列过滤后的值

    Examples:
            delete_filtered_values("field_1")

    Args:
        field: 数据列列名

    Returns:
        None
    """
    py_client.ai_system["industry_standard"].delete_one({"label": label})

def get_industry_standard(label):
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
    return py_client.ai_system["industry_standard"].find_one({"label": label})


def list_all_industry_name():
    """
    获取所有field的名称

    Returns:
        field : list
        example: ["企业基本信息","企业股东及出资信息","企业主要管理人员信息"]
    """
    return [x['label'] for x in py_client.ai_system["industry_standard"].find()]

if __name__=='__main__':
    print(list_all_industry_name())
