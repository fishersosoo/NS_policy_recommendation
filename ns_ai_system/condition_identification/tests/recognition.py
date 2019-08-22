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

    # # 多个跑
    # for j in range(1, 10):
    #     print(j)
    #     with open(os.path.join(policy_file_dir,policy_file_list[j]), encoding="utf8") as f:
    #         text = f.read()
    #     paragraph_extract_output = paragraph_extract(text)
    #     triples, tree, all_sentence = triple_extract(paragraph_extract_output)
    #     fields.extend([x['fields'] for x in triples])
    #     relation.extend([x['relation'] for x in triples])
    #     value.extend([x['value'] for x in triples])
    #     sentence.extend([x['sentence'] for x in triples])
    #
    # pd.DataFrame({"fields": fields, "relation": relation,'value':value,'sentence':sentence}).to_csv("输出结果.csv", index=False)
    # pd.DataFrame({"sentence":sentences,"length":[len(x) for x in sentences]}).to_csv("输出句子.csv",index=False)



# 单个跑
#     with open(os.path.join(policy_file_dir,"申请高管人才奖办事指南"), encoding="utf8") as f:
#         text = f.read()
#     paragraph_extract_output = paragraph_extract(text)
#     triples, all_sentence = triple_extract(paragraph_extract_output)
#     print(triples)
#     print(all_sentence)

    # 多个跑分数
    true_df = pd.read_csv(true_file,encoding = 'gbk')
    score_record = open(score_file, 'a')
    #
    # 计算
    # a = []
    # b = []
    # for j in range(0,len(policy_file_list)):
    #     print(j)
    #     a.append(policy_file_list[j])
    #     with open(os.path.join(policy_file_dir,policy_file_list[j]), encoding="utf8") as f:
    #         text = f.read()
    #     doc = Document.paragraph_extract(text)
    #     b.append(doc.title)
    #
    # pd.DataFrame({'文件':a,'标题':b}).to_csv("测试标题.csv",index=False)

    for j in range(0, len(policy_file_list)):
        print(policy_file_list[j])
        with open(os.path.join(policy_file_dir,policy_file_list[j]), encoding="utf8") as f:
            text = f.read()
        doc = Document.paragraph_extract(text)
        print(doc.get_industry(text))

    # print('------------')
    # for j in range(0, len(policy_file_list)):
    #     print(policy_file_list[j])
    #     with open(os.path.join(policy_file_dir,policy_file_list[j]), encoding="utf8") as f:
    #         text = f.read()
    #     doc = Document.paragraph_extract(text)
    #     print(doc.title)
    #     triples = doc.triple_extract()
    #     for triple in triples:
    #         print(triple.text)
    #         print(triple.type)
    #         print('\n')
    #         for t in triple.clauses:
    #             print(t)
    #             print('\n')
