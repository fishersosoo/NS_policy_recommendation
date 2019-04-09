from condition_identification.util.string_process import getNumofCommonSubstr
from condition_identification.util.specialcondition_identify import idf_nums
def search_field_sameword(fields,sentence):
    field_list=[]
    for field in fields:
        has_word_count=getNumofCommonSubstr(field,sentence)[1]
        if has_word_count>=2:# 因为这样ke'y
            field_list.append(field)
    return field_list

def search_by_relative_pos(value_dict, field_dict, keyword):
    """确定field 和 value

    先找到keyword的下标，然后通过下标先向前遍历再向后遍历，
    找是否有某个keyword的值同时在value_dict和field_dict
    如果没有的话就用value_dic值来表示field

    Args:
        value_dict: dict
        field_dict: dict
        keyword: list

    Returns:
        value_field: dic
    """
    value_field = {}
    is_explicit_field={}
    has_field = False
    for key in value_dict:
        pos = keyword.index(key)
        for i in range(len(keyword)):
            # 它要同时在value_dict和field_dict中
            if pos - i > -1 and keyword[pos - i] in field_dict:  # 向前遍历，keyword是否在在field_dic
                database_key = field_dict[keyword[pos - i]]
                if database_key in value_dict[key]:     # 判断在value_dic
                    value_field[key] = [database_key]
                    del field_dict[keyword[pos - i]]    # 找到一个就删掉他对应的field_dic里的值，防止重复
                    has_field = True
                    break
            if pos + i < len(keyword) - 1 and keyword[pos + i] in field_dict:  # 向后遍历，keyword是否在在field_dic
                database_key = field_dict[keyword[pos + i]]
                if database_key in value_dict[key]:  # 判断在value_dic
                    value_field[key] = [database_key]
                    has_field = True
                    del field_dict[keyword[pos + i]]    # 找到一个就删掉他对应的field_dic里的值，防止重复
                    break
        is_explicit_field[key] = True
        if not has_field:   # 如果没有找到匹配的field，就用 value_dic 值代替field 值
            value_field[key] = value_dict[key]
            if idf_nums(key):
                is_explicit_field[key]=False


    return value_field,is_explicit_field