from pyhanlp import *

keywords = ['奖', '奖励', '资助', '补贴', '补助', '支持', '资金']
def identify_quantifier(parse_words, i, interval):
    flag = False
    m_flag = False
    q_flag = False
    if i < 0:
        i = 0

    while i < len(parse_words) and i <= i + interval:
        term = parse_words[i]
        if str(term.nature) == 'm' or str(term.nature) == 'mq':
            m_flag = True
        if str(term.nature) == 'q':
            q_flag = True
        if m_flag and q_flag:
            flag = True
            break
        i += 1
    return flag


# 识别优惠
def identify_bonus(word):
    flag = False
    parse_words = HanLP.segment(word)
    for i in range(len(parse_words)):
        term = parse_words[i]
        for key in keywords:
            if key in term.word:
                # 加入量词的查找，取关键词所在的前后几个词之内看是否存在量词
                if identify_quantifier(parse_words, i - 10, 10) == False:
                    flag = identify_quantifier(parse_words, i, 10)
                else:
                    flag = True
    return int(flag)

if __name__=='__main__':
    print(identify_bonus('奖励100万元'))