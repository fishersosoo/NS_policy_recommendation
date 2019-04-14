# coding=utf-8
import json

from condition_identification.bonus_identify.DocTree import *
from condition_identification.rdf_triple.triple_tree import construct_tripletree


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
    triples, tree = construct_tripletree(tree)
    tree.show()
    return triples


if __name__ == '__main__':
    import os
    import pandas as pd

    file_dir = r"F:\\txt\\txt"
    tester = pd.read_csv(r'G:\\QQ文件\\政策标注.csv', engine='python')
    acc_result = []
    all_true = 0
    all_count = 0

    for j in range(2, 40):
        score_record = open('score.txt', 'a')
        file_tester = tester[tester['序号'] == j]
        if file_tester.shape[0] == 0:
            continue
        with open(os.path.join(file_dir,str(j)+".txt"), encoding="utf8") as f:
            text = f.read()
        paragraph_extrac_output = paragraph_extract(text)
        triples = triple_extract(paragraph_extrac_output)
        if not triples:
            continue
        print(triples)
        # import pickle
        # f=open('0.pkl','rb')
        # pickle.dump(triples,f)
        # triples=pickle.load(f)

        def isin(a, b):
            isin_flag = True
            for w in a:
                if w not in b:
                    isin_flag = False
                    break
            return isin_flag
        tr = 0
        file_tester_len = file_tester.shape[0]
        for i in range(file_tester_len):
            sentence = file_tester['原文'].values[i]
            target = file_tester['列名'].values[i]
            is_none = True
            pre = []
            for triple in triples:
                if isin(triple['sentence'],sentence) or isin(sentence, triple['sentence']):
                    is_none = False
                    pre = triple['fields']
                    # 标注时把行业领域统一标成了经营业务范围
                    if '行业领域' in pre:
                        pre.append('经营业务范围')
                    # 因为同一个句子可能有多个实体，所以需要遍历所有实体
                    if target in pre:
                        print(sentence)
                        tr += 1
                        break

            if target == 'None':
                if is_none:
                    tr += 1
        acc_result.append(tr/file_tester_len)
        all_true += tr
        all_count += file_tester_len
        print("%s 文件准确率 %f" % (str(j), tr/file_tester_len))
        score_record.write("%s 文件准确率 %f" % (str(j), tr/file_tester_len))
        score_record.write('\n')
        import numpy as np
        print("总文件准确率 %f"%np.mean(np.array(acc_result)))
        score_record.write("总文件准确率 %f" % np.mean(np.array(acc_result)))
        score_record.write('\n')
        print("all_count:%s\tall_true:%s\tprecision %f" % (all_count, all_true,all_true/all_count))
        score_record.write("all_count:%s\tall_true:%s\tprecision %f" % (all_count, all_true, all_true/all_count))
        score_record.write('\n')
        score_record.close()
