from pyhanlp import *
from condition_identification.args import NUMS
danwei = {'九':9, '八':8, '七':7, '六':6, '五':5, '四':4, '三':3, '二':2, '一':1, '零':0}

# 计算中文数字值
def cal(inStr):
    import re
    sum = 0
    if len(inStr) == 0:  # 处理空字段，如：一亿零一， “万” 字段为空
        return sum
    if inStr.isdigit():
        return int(inStr)
    inStr = inStr.replace('零', '')
    try:
        qian = re.findall('(.)千', inStr)[0][0]  # 正则匹配（）千，若未匹配到则 “千” 为 零
    except IndexError:
        qian = '零'
    try:
        bai = re.findall('(.)百', inStr)[0][0]  # 正则匹配（）百，若未匹配到则 “百” 为 零
    except IndexError:
        bai = '零'
    try:
        shi = re.findall('(.)十', inStr)[0][0]  # 正则匹配（）十， 字符串包含“十”，则“十”为其前面一个数，若 “十” 前无数字，则 “十” 为 一；字符串不包含“十”，则“十” 为 零
    except IndexError:                                         
        shi = '一' if '十' in inStr else '零'
    if len(inStr)==0:
        ge='零'
    else:
        ge = inStr[-1] if inStr[-1] not in ['十','百','千','万','亿'] else '零'
    sum = danwei.get(qian)*1000+danwei.get(bai)*100+danwei.get(shi)*10+danwei.get(ge)
    return sum
# 拆分中文数字并计算总值
def zh_to_num(tmp):
    if '亿' in tmp:
        yi = tmp.split('亿')[0]
        if len(tmp.split('亿')[1]) is 0:
            wan, ge = '', ''
        if '万' in tmp:
            wan = tmp.split('亿')[1].split('万')[0]
            ge = tmp.split('亿')[1].split('万')[1] if len(tmp.split('亿')[1].split('万')[1]) != 0 else ''
    elif '万' in tmp:
        yi = ''
        wan = tmp.split('万')[0]
        ge = tmp.split('万')[1] if len(tmp.split('万')[1]) != 0 else ''
    else:
        yi = ''
        wan = ''
        ge = tmp
    cal(wan) * 10000
    cal(ge)
    num = cal(yi)*100000000+cal(wan)*10000+cal(ge)
    return num

def get_num(word):
    number = ''
    for i in range(len(word)):
        try:
            number = zh_to_num(word[0:i])
        except:
            print(word[0:i])
            break
    return number



def extract_num(triple):
    if triple.field[0] in NUMS:
        line=triple.value
        number=''
        i=0
        print(triple.value)
        segment=HanLP.segment(line)
        while i<len(segment)-1:
            term =  segment[i]
            nextterm = segment[i+1]
            nature = str(term.nature)
            word = term.word
            nextnature = str(nextterm.nature)
            nextword = nextterm.word
            if nature == 'm'and (nextnature == 'q' or nextnature == 'l'):
                line = word+nextword
                number=str(get_num(line))
                break
            i+=1
        # 有一定可能性number为空，可能导致报错
        triple.value=number
        print(triple.value)
        if number=='':
            print('*****************************')
            print(line)
            print('*****************************')


    return triple








if __name__ == '__main__':
    a=['1','2']
    b=['3','4']
    print(get_num('第三方'))
