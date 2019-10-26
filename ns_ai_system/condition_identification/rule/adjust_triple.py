error_cases = ['办公地址', '其他违法记录', '申报企业','统计关系','财务']
field_cases = ['变更事项','变更事项代码','变更前内容','变更后内容','变更时间']

def adjust_byrule(triple):
    flag1 = adjust_byvalue(triple)
    flag2 = adjust_byfield(triple)
    if flag1 or flag2 :
        return None
    else:
        return triple


def adjust_byvalue(triple):
    flag = False
    for error_case in error_cases:
        if error_case in triple.value:
            flag = True
            break
    return flag
def adjust_byfield(triple):
    flag = False
    for field_case in field_cases:
        for field in triple.fields:
            if field_case in field:
                flag = True
                break
    return flag