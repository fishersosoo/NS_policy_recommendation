# coding=utf-8

import re
from condition_identification.util.sentence_preprocess import filter_punctuation
from bisect import bisect_left


def insert(word, wait_word_id, wait_word):
    """" 把word 根据id插入到合适的位置

    抽取关键词，不能改变关键词组里词的位置顺序，
    因此将词按照id大小插入合适的位置，
    用二分法找到插入位置。

    Args:
        word: str ，待插入的词
        wait_word:list ,候选词组成的list，有定中关系的词
        wait_word_id:候选词组的id

    Returns:
        wait_word_id: list,
        wait_word: list，有定中关系的词
            Examples: wait_word: ['广州市', '南沙区', '范围', '内']

    """
    if word.ID in wait_word_id:
        return wait_word_id, wait_word
    # word.ID 和 word.LEMMA 插入到合适的位置
    pos = bisect_left(wait_word_id, word.ID)
    wait_word_id.insert(pos, word.ID)
    wait_word.insert(pos, word.LEMMA)
    return wait_word_id, wait_word


# 如果定中之间杂夹了定中分不出来
def extract_keyword(sentence, len_threshold):
    """抽取政策条件语句的关键词

       利用 pyhanlp 对政策语句进行分词和词法分析，获取关键词

       Args:
           sentence: str
               Examples: '工商注册地、税务征管关系及统计关系在广州市南沙区范围内；'
           len_threshold: int,

       Returns:
           result_word: list,政策语句的关键词
               Examples:  ['工商注册地', '征管关系', '统计关系', '广州市南沙区范围内']

       """
    from pyhanlp import HanLP
    lines = sentence.split('；')
    result_word = []
    for line in lines:
        b = HanLP.parseDependency(line)
        word_array = b.getWordArray()
        wait_word = []
        history_word = []
        wait_word_id = []
        id_last = 0
        # 词法分析，利用定中关系对分词的结果进一步提取出关键词
        for word in word_array:
            word.LEMMA, word.HEAD.LEMMA = filter_punctuation(word.LEMMA, word.HEAD.LEMMA)
            if word.DEPREL == '定中关系':
                if abs(word.ID - word.HEAD.ID) >= 5:  # 隔太远，即使定中关系也不会成一个词
                    continue
                wait_word_id, wait_word = insert(word, wait_word_id, wait_word)
                wait_word_id, wait_word = insert(word.HEAD, wait_word_id, wait_word)
                id_last = word.HEAD.ID  # 与定中关系有关的id最大的词的下标
            elif word.ID >= id_last:  # word.ID 大于等于有定中关系的词的最大的下标就把之前的词连起来
                complete_word = ''.join(wait_word)
                if complete_word != '':
                    result_word.append(complete_word)
                    history_word.extend(wait_word)
                    wait_word = []
                    wait_word_id = []
            if word.DEPREL != '定中关系' and 'n' in word.POSTAG and len(  # 把大于阈值并且不在历史词里的名词加进去
                    word.LEMMA) > len_threshold and word.LEMMA not in history_word:
                result_word.append(word.LEMMA)
        complete_word = ''.join(wait_word)  # 最后一个词在最后面的时候
        if complete_word != '':
            result_word.append(complete_word)
    return result_word


if __name__ == "__main__":
    print(extract_keyword('卫生部将听取各方意见修订食品安全标准。新华网北京8月29日电 (周英峰，聂妍婧)中国卫生部副部长陈啸宏29日表示，卫生部会同有关部门已正式启动食品安全标准的整合工作。在标准修订过程中，将广泛听取方方面面的意见。陈啸宏在此间举行的“2009·食品药品安全责任论坛”上说，这次整合工作将重点解决标准缺失、重复和矛盾的问题，逐步建立与中国社会经济发展相适应，与国际食品标准体系相协调，满足保障人民健康需要的食品安全标准体系。陈啸宏表示，标准修订过程中，将广泛借鉴国际经验，充分运用食品安全风险评估结果，将食品致病性微生物、农药残留、微生物残留、重金属污染物质的限量标准以及食品添加剂的修订作为优先领域。陈啸宏说，卫生部将邀请各个领域的相关专家参加标准修订工作，也欢迎企业参与其中。修订后的标准将形成草案，广泛征求社会的意见，包括听取国际组织和相关国家的意见，完全按照WTO的要求进行。陈啸宏介绍说，中国将加强食品安全风险监测评估的体系建设，力争用2年左右时间在全国建立起覆盖食品生产经营各环节、从城市到农村的食品污染物、食源性疾病监测和总膳食调查体系。建立国家食品安全风险评估中心，在有条件的省份设立分中心，健全食品安全风险评估体系。陈啸宏最后透露，卫生部将继续会同有关部门深入推进食品安全整顿工作。继续发布违反添加非食用物质和滥用食品添加剂名单，查处研制、生产、销售、使用非食用添加物质的行为。此次“食品药品安全责任论坛”由中国国际跨国公司研究会与联合国贸发会议、联合国开发计划署、联合国环境规划署、联合国工业发展组织和联合国全球契约组织共同举办。', 2))
