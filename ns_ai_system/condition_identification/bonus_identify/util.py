def str_to_list(text):
    """
    读取字符串

    :param text:
    :return:
    """
    text_lines = []
    cond_flag = False
    word = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    next_word_index = 0
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
        if line[0] in strange_dict:
            line = strange_dict[line[0]] + line[1:]
        if line[0] in word and '、' in line and '条件' in line:
            if line.find('条件') - line.find('、') < 5:
                cond_flag = True
                next_word_index = word.index(line[0]) + 1

        if cond_flag:
            if word[next_word_index] + '、' in line:
                cond_flag = False

        if cond_flag:
            text_lines.append(line)

    return text_lines


def file_to_list(file_path):
    """
    读取文件成list

    :param file_path:
    :return:
    """
    with open(file_path, 'r', encoding='utf8') as f:
        text = f.read()
        return str_to_list(text)
