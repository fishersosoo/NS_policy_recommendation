
def searchbyrelativepos(valuedict,fielddict,keyword):
    result = {}
    hasfield = False
    for key in valuedict:
        pos = keyword.index(key)
        for i in range(len(keyword)):
            # 它要同时在fieldict和valuedict中
            if pos - i > -1 and keyword[pos - i] in fielddict:
                database_key = fielddict[keyword[pos - i]]
                if database_key in valuedict[key]:
                    result[key] = [database_key]
                    del fielddict[keyword[pos - i]]
                    hasfield = True
                    break
            if pos + i < len(keyword) - 1 and keyword[pos + i] in fielddict:
                database_key = fielddict[keyword[pos + i]]
                if database_key in valuedict[key]:
                    result[key] = [database_key]
                    hasfield = True
                    del fielddict[keyword[pos + i]]
                    break
        if not hasfield:
            result[key] = valuedict[key]
    return result

