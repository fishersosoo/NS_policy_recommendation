def search_by_relative_pos(value_dict, field_dict, keyword):
    result = {}
    has_field = False
    for key in value_dict:
        pos = keyword.index(key)
        for i in range(len(keyword)):
            # 它要同时在value_dict和field_dict中
            if pos - i > -1 and keyword[pos - i] in field_dict:
                database_key = field_dict[keyword[pos - i]]
                if database_key in value_dict[key]:
                    result[key] = [database_key]
                    del field_dict[keyword[pos - i]]
                    has_field = True
                    break
            if pos + i < len(keyword) - 1 and keyword[pos + i] in field_dict:
                database_key = field_dict[keyword[pos + i]]
                if database_key in value_dict[key]:
                    result[key] = [database_key]
                    has_field = True
                    del field_dict[keyword[pos + i]]
                    break
        if not has_field:
            result[key] = value_dict[key]
    return result
