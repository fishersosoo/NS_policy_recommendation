def adjust_database_keyword_byrule(keywords):
    result=[]
    for s in keywords:
        s = s.replace('企业', '')
        if s :
            result.append(s)
    return result