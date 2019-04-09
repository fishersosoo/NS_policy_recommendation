from condition_identification.name_entity_recognition.extract_name_entity import get_field_value
from condition_identification.relation_predict.extract_relation import get_relation
from condition_identification.rdf_triple.triple import Triple
from condition_identification.bonus_identify.DocTree import *
from condition_identification.util.search import search_field_sameword
def construct_tripletree(tree):
    """提取条件树

    根据传入的指南树进行filed,value,relation的拆分
    并且组装成and/or关系
    其主要关系图查看uml.jpg

    Args:
        tree: Tree 指南拆解后的树

    Returns:
        tree: Tree 对输入的tree的node内容进行改写结果
    """
    triples = []
    for node in tree.expand_tree(mode=Tree.DEPTH):
        sentence = "。".join(tree[node].data)
        # 解决and/or
        # 非and/or节点的tag值为原先值，即政策文本
        if not tree[node].is_leaf():
            if "之一" in sentence or '其二' in sentence:
                tree[node].tag = 'or'
            else:
                tree[node].tag = 'and'
        else:
            # 叶子节点不改变tag
            pass

        # 解决三元组
        triples_dict,is_explicit_field = get_field_value(sentence)
        for key in triples_dict:
            relation, presentence = get_relation(sentence, key)
            triple = Triple()
            triple.relation = relation
            triple.value = key
            triple.sentence = presentence
            if is_explicit_field[key]:
                triple.filed = triples_dict[key]
            else:
                triple.filed = search_field_sameword(triples_dict[key], presentence)

            if triple.filed:
                triples.append(triple.to_dict())
            print(presentence)
            print(triple)
        tree[node].data = triples
    return triples,tree