# coding=utf-8
def search_by_relative_pos(value_dict, field_dict, keyword):
    """确定field 和 value

    Args:
        value_dict: dic
        field_dict: dic
        keyword: list
    Returns:
        dic
    """
    result = {}
    has_field = False
    for key in value_dict:
        pos = keyword.index(key)
        for i in range(len(keyword)):
            # 它要同时在value_dict和field_dict中
            if pos - i > -1 and keyword[pos - i] in field_dict:  # 判断下标满足要求，并且在field_dic
                database_key = field_dict[keyword[pos - i]]
                if database_key in value_dict[key]:     # 判断在value_dic
                    result[key] = [database_key]
                    del field_dict[keyword[pos - i]]
                    has_field = True
                    break
            if pos + i < len(keyword) - 1 and keyword[pos + i] in field_dict:  # 判断下标满足要求，并且在field_dic
                database_key = field_dict[keyword[pos + i]]
                if database_key in value_dict[key]:  # 判断在value_dic
                    result[key] = [database_key]
                    has_field = True
                    del field_dict[keyword[pos + i]]
                    break
        if not has_field:   # 如果没有找到匹配的field，就用 value_dic
            result[key] = value_dict[key]
    return result
