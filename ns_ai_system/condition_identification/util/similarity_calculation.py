from condition_identification.util.distance_calculations import cos_sim
from condition_identification.util.string_process import getNumofCommonSubstr
from condition_identification.args import similarity_value


def _search_max_word(value_word, value_encode, line_encode, line):
    """找到与keyword相似度最高的值

     Args:
         value: list ，某个field值对应的数据库里的部分value数据
         value_encodes: numpy.ndarry ,value值转化的bert词向量
         line_encode:  numpy.ndarry ,keyword对应的bert词向量
         line:  str， 政策条件抽取的keyword
             Examples:
                 value: ['建筑业', '邮政业', '仓储', '公共设施', '其他服务业', '交通运输', '娱乐业']
                 line: ['工商注册地']

     Returns:
         has_max_word: bool ,是否找到相似度满足要求的value值

     """
    from pyhanlp import HanLP
    max_value = 0
    max_word = ''
    has_max_word = False
    for word, value_encode in zip(value_word, value_encode):
        word = word.strip()
        flag = False
        for term in HanLP.segment(word):  # 必须要有相同的词才可以
            if term.word in line:
                flag = True
                break
        if flag:
            value = cos_sim(line_encode, value_encode)
            if max_value < value:
                max_value = value
                max_word = word
            if max_word != '' and max_value > similarity_value:
                has_max_word = True
                break

    return has_max_word


def compare_similarity(line, value_word, value_encode, bert_client):
    """计算keyword与filed对应的数据库列值的相似度，找到相似度最高的列值

    利用bert获得词向量，计算相似度，找到相似度最高的那个

    Args:
        value_word: list ，某个field值对应的数据库里的value数据
        line:  str ，keyword,政策条件抽取出的关键词
        value_encode: list, value值对应的Bert向量
        bert_client: 获得词向量的bert 工具
            Examples:
                value: ['建筑业', '邮政业', '仓储', '公共设施', '其他服务业', '交通运输', '娱乐业']
                line: ['工商注册地']
    Returns:
      max_value:float  相似度最高的相似度值
      max_word：str    相似度最高的那个词

    """
    line_encode = bert_client.encode([line])
    has_max_word = _search_max_word(value_word, value_encode, line_encode, line)
    return has_max_word


def field_compare_similarity(line, vector, field, field_vec_dict):
    """找到与政策条件关键词相似度最高的field值

    Args:
        line: str，政策条件抽取的一个关键词
        vector: numpy.ndarray ,line 所对应的 bert词向量
        field: set,field集合
        field_vec_dict: dict,field与其对应的bert词向量字典

            Examples:  line : '广州市南沙区范围内'
                       field: {'网站首页地址', '网站（网店）名称', '主分类号', '申请（专利权）人', '变更内容'}
                       field_vec_dict: {'营业总收入’：array(768*1),'代理机构': array(768*1)}

    Returns:
        max_value: float,最高的相似度值
        max_word: str,与关键词相似度最高的field值

    """
    max_value = 0
    max_word = ''
    # 找出与line相似度最高的field 以及他们的相似度
    for word in field:
        has_word_count = getNumofCommonSubstr(word, line)[1]
        if has_word_count > 0:
            word_vec = field_vec_dict[word]
            value = cos_sim(vector, word_vec)  # 获取他们的相似度
            if max_value < value:
                max_value = value
                max_word = word
    return max_value, max_word
