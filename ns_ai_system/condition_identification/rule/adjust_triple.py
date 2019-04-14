error_cases = ['办公地址', '其他违法记录', '申报企业']


def adjust_byrule(triple):
    for error_case in error_cases:
        if triple.value in error_case:
            print('dsdsds')
            triple.filed = None
            break
    return triple