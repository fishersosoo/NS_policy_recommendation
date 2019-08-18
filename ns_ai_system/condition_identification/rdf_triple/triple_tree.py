from condition_identification.name_entity_recognition.extract_name_entity import get_field_value
from condition_identification.relation_predict.extract_relation import get_relation
from condition_identification.rdf_triple.triple import Triple
from condition_identification.doctree_contruction.DocTree import *
from condition_identification.util.search import search_field_sameword
from condition_identification.rule.adjust_triple import adjust_byrule
from condition_identification.rule.adjust_number import extract_num
from condition_identification.content_filter.wordFilter import promiseFilter,tiaojianFilter
from condition_identification.util.sentence_preprocess import filter_punctuation_include_content
from condition_identification.content_filter.talentFilter import talentFilter
import uuid


def constructTriple(tree):
    """构建三元组树

    Args:
        tree: Tree 指南拆解后的树

    Returns:
        triples: list, 抽取到的三元组列表
        tree: Tree 对输入的tree的node内容进行改写结果
            Examples:
                triples: [{'fields': ['地址'], 'relation': '位于', 'value': '南沙',
                           'sentence': '工商注册地、税务征管关系及统计关系在南沙新区范围内'}]
    """

    sentences = getSentencesByLeave(tree)

    sentenceWithID = contructSentenceWithID(sentences)

    alltriples = constructTripleBySentence(sentenceWithID)

    return alltriples, sentenceWithID

def getSentencesByLeave(tree):
    sentences = []
    for node in tree.expand_tree(mode=Tree.DEPTH):
        sentences.extend(tree[node].data)
    return sentences

def constructTripleBySentence(sentenceWithID):
    """构建满足条件的句子以及全部句子的集合

    根据传入的sentence，组装{id:sentence},如果该句子构建出三元组，则该三元组会储存当前句子的id

    Args：
        sentenceWithID：dict 储存所有句子

    Returns:
        triples:list 构建的三元组列表，一个句子可能会有多个三元组
    """
    triples = []
    for uid in sentenceWithID:
        sentence = sentenceWithID[uid]
        sentences = sentenceFilter([sentence])
        for sentence in sentences:
            if sentence:
                triple = constructTriples(sentence, uid)
                triples.extend(triple)
    return triples

def contructSentenceWithID(sentences):
    sentenceWithID = {}
    for sentence in sentences:
        unique_id = str(uuid.uuid1())
        sentenceWithID[unique_id] = sentence
    return sentenceWithID

def sentenceFilter(sentences):
    # 1.人才的句子过滤
    result = []
    sentences = talentFilter(sentences)
    if len(sentences) == 0:
        return result

    sentence = "。".join(sentences)
    # 2.句子粒度切分
    sentence = filter_punctuation_include_content(sentence)
    sentence = sentence.replace('；', "。")
    sentences = sentence.split("。")

    # 3.“承诺”和“条件”句子过滤
    result = [s for s in sentences if promiseFilter(s) and tiaojianFilter(s)]

    return result

def constructTriples(sentence, unique_id):
    """提取三元组

    Args:
        sentence: Str 需要拆解的三元组句子
        unique_id:Str 对应的句子id，同一个句子的三元组共用一个id

    """
    # 解决三元组
    triples = []
    triples_dict, is_explicit_field = get_field_value(sentence)
    for key in triples_dict:
        relation = get_relation(sentence, key)
        triple = Triple()
        triple.relation = relation
        triple.value = key
        triple.sentence = sentence
        triple.sentence_id = unique_id
        # 过滤候选field
        if is_explicit_field[key]:
            triple.field = triples_dict[key]
        else:
            triple.field = search_field_sameword(triples_dict[key], sentence)
        # 人工规则
        triple = adjust_byrule(triple)
        # 提取单纯数字
        if triple.field:
            triple = extract_num(triple)
            triples.append(triple.to_dict())
    return triples
