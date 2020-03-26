# coding=utf-8
def adjust_database_keyword_byrule(keywords):
    """对数据库值进行处理

    Args:
        keywords: list，数据库列值

    """
    result = [s.replace('企业', '') for s in keywords]
    result = list(filter(None, result))
    return result


