from condition_identification.bonus_identify.DocTree import *
from condition_identification.name_entity_recognition.reg import get_field_value
from condition_identification.relation_predict.extract_relation import get_relation


# coding=utf-8
def paragraph_extract(text):
    """抽取指南

    根据指南的标题结构，抽取政策条件，并构造结构树

    Args：
        text: str 政策文本

    Returns：
        tree: Tree 构造后的政策树


    """
    doc_tree = DocTree()
    doc_tree.construct(text)
    tree = doc_tree.get_tree()
    return tree


class Triple:
    """保存三元组
    用于保存三元组，存储内容包括(s, r, o)三元组、每个三元组对应的原文

    Attributes:
        filed: [] value可能对应的filed
        relation:str 关系“大于、小于、位于、是、否”
        value: str 值
        sentence: str 对应原文

    """

    def __init__(self):
        self.filed = []
        self.relation = ''
        self.value = ''
        self.sentence = ''

    def to_dict(self):
        """
        转化为dict

        :return:
        """
        return {"fields": self.filed, "relation": self.relation, "value": self.value, "sentence": self.sentence}

    def __repr__(self):
        """打印三元组
        """
        return str((self.filed, self.relation, self.value))


def triple_extract(tree):
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
        triples_dict = get_field_value(sentence)
        for key in triples_dict:
            relation, presentence = get_relation(sentence, key)
            triple = Triple()
            triple.relation = relation
            triple.value = key
            triple.sentence = presentence
            triple.filed = triples_dict[key]
            triples.append(triple.to_dict())
        tree[node].data = triples

    tree.show()
    return triples


if __name__ == '__main__':
    with open(r"F://txt//txt//29.txt",encoding="utf8") as f:
        text = f.read()
    paragraph_extrac_output = paragraph_extract(text)

    triples = triple_extract(paragraph_extrac_output)
