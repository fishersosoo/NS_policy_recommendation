from condition_identification.api.text_parsing import Document
from condition_identification.util.string_process import getNumofCommonSubstr
import os
import pandas as pd
import numpy as np

def isin(a, b):
    isin_flag = True
    for w in a:
        if w not in b:
            isin_flag = False
            break
    return isin_flag



def get_acc_pre(true_df_txt, triples):
    true_df_txt_len = true_df_txt.shape[0]
    predict_len = len(triples)
    txt_tr = 0 # 用来算准确率
    triple_tr = 0 # 用来算召回率,一个句子中多个实体三元组都满足
    for i in range(true_df_txt_len):
        sentence = true_df_txt['原文'].values[i]
        target = true_df_txt['列名'].values[i]
        is_none = True
        acc_flag=True
        for triple in triples:
            min_len=min(len(triple['sentence']),len(sentence))
            if getNumofCommonSubstr(triple['sentence'], sentence)[1] > min_len-5:
                is_none = False
                pre = triple['fields']
                # 标注时把行业领域统一标成了经营业务范围
                if '行业领域' in pre:
                    pre.append('经营业务范围')
                # 因为同一个句子可能有多个实体，所以需要遍历所有实体
                if target in pre:
                    print(sentence)
                    triple_tr += 1
                    if acc_flag:
                        txt_tr+=1
                        acc_flag=False


        if target == 'None' and is_none:
            txt_tr += 1
            predict_len += 1
            triple_tr += 1
    return txt_tr,triple_tr,predict_len



if __name__ == '__main__':
    policy_file_dir = 'new_policy_withtitle/'
    policy_file_list = os.listdir(policy_file_dir) #列出文件夹下所有的目录与文件
    true_file = r'/data/政策标注.csv'
    score_file = 'score0603.txt'
    fields = []
    relation = []
    value = []
    sentence = []


    print('------------')
    for j in range(0, len(policy_file_list)):
    # for j in range(0, 1):
        with open(os.path.join(policy_file_dir,policy_file_list[j]), encoding="utf8") as f:
            text = f.read()
        doc = Document.paragraph_extract(text)
        print(doc.title)
        print(doc.industries)
        # doc.triple_extract()
        # triples =doc.sentences
        # for triple in triples:
        #     print(triple.text)
        #     print(triple.type)
        #     print('\n')
        #     for t in triple.clauses:
        #         print(t)
        #         print('\n')
