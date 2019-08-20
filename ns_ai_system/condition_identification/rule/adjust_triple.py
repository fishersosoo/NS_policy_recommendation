error_cases = ['办公地址', '其他违法记录', '申报企业','统计关系','财务']


def adjust_byrule(triple):
    for error_case in error_cases:
        if error_case in triple.value:
            triple.fields = None
            break
    return triple