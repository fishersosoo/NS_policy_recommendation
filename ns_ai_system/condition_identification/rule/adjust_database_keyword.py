# coding=utf-8
def adjust_database_keyword_byrule(keywords):
    """对数据库值进行处理

    Args:
        keywords: list，数据库列值

    """
    result = []
    for s in keywords:
        s = s.replace('企业', '')
        if s:
            result.append(s)
    return result
