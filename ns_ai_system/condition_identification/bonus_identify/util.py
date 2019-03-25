# 读取字符串
def str_tolist(str):
    html_list = []
    cond_flag=False
    word=['一','二','三','四','五','六','七','八','九','十']
    nexthword_index=0
    strange_dict={
     '壱':'一',
    '弐':'二',
    '参':'三',
    '四':'四',
    '伍':'五',
    '〇':'零'
    }
    for line in str.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line[0] in strange_dict:
            line = strange_dict[line[0]] + line[1:]
        if line[0] in word and '、' in line and '条件' in line:
            if line.find('条件') - line.find('、') < 5:
                cond_flag = True
                nexthword_index = word.index(line[0]) + 1

        if cond_flag:
            if word[nexthword_index] + '、' in line:
                cond_flag = False

        if cond_flag:
            html_list.append(line)

    return html_list


# 读取文件成list
def file_tolist(file):
    html_list = []
    cond_flag=False
    word=['零','一','二','三','四','五','六','七','八','九','十']
    strange_dict={
     '壱':'一',
    '弐':'二',
    '参':'三',
    '四':'四',
    '伍':'五',
    '〇':'零'
    }
    nexthword_index=0
    with open(file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            if line[0]in strange_dict:
                line=strange_dict[line[0]]+line[1:]
            if  line[0] in word and '、' in line and '条件' in line :
                if line.find('条件')-line.find('、')<5:
                    cond_flag = True
                    nexthword_index = word.index(line[0]) + 1

            if cond_flag:
                if word[nexthword_index] + '、' in line:
                    cond_flag = False

            if cond_flag:
                html_list.append(line)
    return html_list