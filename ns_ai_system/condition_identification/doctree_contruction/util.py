# coding=utf-8


def str_to_list(text):
    """读取字符串

    Args:
        text: list 政策文本内容

    Return:
        text: list 拆解后只剩下政策条件的内容
    """
    text_lines = []
    cond_flag = False
    word = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    next_word_index = 0  # 用来标记申请条件的下一个标题序号，以作结束
    strange_dict = {
        '壱': '一',
        '弐': '二',
        '参': '三',
        '四': '四',
        '伍': '五',
        '〇': '零'
    }
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 对奇怪文字进行修正
        if line[0] in strange_dict:
            line = strange_dict[line[0]] + line[1:]
        # 政策条件内容的开始标记
        if line[0] in word and '、' in line and '条件' in line:
            if line.find('条件') - line.find('、') < 5:
                cond_flag = True
                next_word_index = word.index(line[0]) + 1

        if cond_flag:
            # 政策条件内容的结束标记
            if word[next_word_index] + '、' in line:
                cond_flag = False
            else:
                text_lines.append(line)

    return text_lines


def file_to_list(file_path):
    """读取文件成list

    读取文件的内容后复用按照内容抽取的方法逻辑

    Args:
        file_path: str 政策文件路径

    Return:

    """
    with open(file_path, 'r', encoding='utf8') as f:
        text = f.read()
        return str_to_list(text)
