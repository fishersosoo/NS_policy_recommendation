from condition_identification.name_entity_recognition.extract_name_entity import get_field_value
from condition_identification.relation_predict.extract_relation import get_relation
from condition_identification.rdf_triple.triple import Triple
from condition_identification.bonus_identify.DocTree import *
from condition_identification.util.search import search_field_sameword
from condition_identification.rule.adjust_triple import adjust_byrule
from condition_identification.rule.adjust_number import extract_num
from treelib.exceptions import DuplicatedNodeIdError
from condition_identification.util.sentence_preprocess import filter_punctuation_include_content
import uuid


def construct_tripletree(tree):
    """提取条件树

    根据传入的指南树进行filed,value,relation的拆分
    并且组装成and/or关系
    其主要关系图查看uml.jpg

    Args:
        tree: Tree 指南拆解后的树

    Returns:
        triples: list, 抽取到的三元组列表
        tree: Tree 对输入的tree的node内容进行改写结果
            Examples:
                triples: [{'fields': ['地址'], 'relation': '位于', 'value': '南沙',
                           'sentence': '工商注册地、税务征管关系及统计关系在南沙新区范围内'}]
    """
    alltriples = []
    all_sentence = {}
    triple_tree = DocTree.copy_tree(tree, '')
    for node in tree.expand_tree(mode=Tree.DEPTH):
        sentence = "。".join(tree[node].data)
        # 判断'or'/'and'关系
        if tree[node].is_leaf():
            triples = construct_sentence_triple(sentence, all_sentence)
            triple_tree[node].tag = 'and'
            triple_tree = split_node(triple_tree, node, triples)
            alltriples.extend(triples)
        else:
            if "之一" in sentence or '其二' in sentence:
                triple_tree[node].tag = 'or'
            else:
                triple_tree[node].tag = 'and'
        # tree[node].data = triples
    return alltriples, triple_tree, all_sentence


def construct_sentence_triple(sentence, all_sentence):
    """构建满足条件的句子以及全部句子的集合

    根据传入的sentence，组装{id:sentence},如果该句子构建出三元组，则该三元组会储存当前句子的id

    Args：
        sentence：str 结构树中叶子节点的内容
        all_sentence：dict 储存所有句子

    Returns:
        triples:list 构建的三元组列表，一个句子可能会有多个三元组
    """
    triples = []
    sentence = filter_punctuation_include_content(sentence)
    # 切分句子粒度
    sentence = sentence.replace('，', "。")
    sentence = sentence.replace('；', "。")
    sentences = sentence.split("。")
    for sentence in sentences:
        unique_id = str(uuid.uuid1())
        # 排除掉符合以下全部申请条件的这些句子。
        if sentence and not ("：" in sentence and '条件' in sentence):
            all_sentence[unique_id] = sentence
            triple = construct_triples(sentence, unique_id)
            triples.extend(triple)
    return triples


def construct_triples(sentence, unique_id):
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
            print(sentence)
            print(triple)
    return triples


def split_node(tree,node,triples):
    unique=0
    for triple in triples:
        try:
            tree.create_node(identifier=tree[node].identifier+'_'+triple['value'],data=triple, tag=[], parent=tree[node].identifier)
        except DuplicatedNodeIdError:
            tree.create_node(identifier=str(unique)+tree[node].identifier + '_' + triple['value'], data=triple, tag=[],
                             parent=tree[node].identifier)
            unique += 1
    return tree
