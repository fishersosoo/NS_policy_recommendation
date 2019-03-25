from bonus_identify.DocTree import *
from name_entity_recognition.reg import getField_Value
from relation_predict.extract_relation import get_relation
# coding=utf-8
class ParagraphExtractOutput:
    """
    用于保存paragraph_extract函数的结果

    """

    def __init__(self):
        raise NotImplementedError("Not Implemented")


def paragraph_extract(text):
    """
    根据指南的标题结构，抽取不同部分信息

    :type text: str
    :param text: 指南文本
    :return 返回ParagraphExtractOutput， 如果指南格式不符合要求则返回None
    """
    tree = DocTree()
    tree.construct(text, 2)
    t = tree.get_tree()
    return t



class Triple:
    """
    用于保存多个条件三元组，存储内容包括了多个(s, r, o)三元组、每个三元组对应的原文、三元组之间的and和or关系

    """
    def __init__(self):
        '''
        f:field
        r:relation
        v:value
        '''
        self.f=[]
        self.r=''
        self.v=''

    def __repr__(self):
        """
        打印结果

        :return:
        """
        raise NotImplementedError("Not Implemented")


def triple_extract(tree):
    """
    提取条件三元组
    :type paragraph_extract_output: ParagraphExtractOutput
    :param paragraph_extract_output: paragraph_extract()的返回
    :return: 返回关系树
    """
    for node in  tree.expand_tree(mode=Tree.DEPTH):
        sentence="。".join(tree[node].data)
        # 解决and/or
        if not tree[node].is_leaf():
            if "之一"in sentence or '其二'in sentence:
                tree[node].tag='or'
            else:
                tree[node].tag = 'and'
        else:
            # 叶子节点不改变tag
            pass

        # 解决三元组
        triples=[]
        triples_dict=getField_Value(sentence)
        for key in triples_dict:
            triple=Triple()
            triple.v=key
            triple.f=triples_dict[key]
            triple.r=get_relation(text,key)
            triples.append(triple)
        tree[node].data=triples
    tree.show()
    return tree





if __name__ == '__main__':
    file_path = r'F:\\txt\\txt\\2.txt'
    text = ""
    try:
        with open(file_path,'r',encoding='utf8') as f:
            text = f.read()
    except:
        pass
    paragraph_extrac_output = paragraph_extract(text)
    triples = triple_extract(paragraph_extrac_output)

