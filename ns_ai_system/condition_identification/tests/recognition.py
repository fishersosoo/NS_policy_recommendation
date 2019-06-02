from condition_identification.api.text_parsing import paragraph_extract
from condition_identification.api.text_parsing import triple_extract
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

    policy_file_dir = r"/data/txt/txt"
    true_file = r'/data/政策标注.csv'
    score_file = 'score0601.txt'

    true_df = pd.read_csv(true_file,encoding = 'gbk')
    score_record = open(score_file, 'a')

    # 计算
    a1=[]
    a2=[]
    a3=[]
    a4=[]
    a5=[]
    a6=[]
    acc_result = []
    rec_result = []
    all_acctrue = 0
    all_rectrue = 0
    all_count = 0
    all_precount=0

    for j in range(0,40):
        true_df_txt = true_df[true_df['序号'] == j]
        if true_df_txt.shape[0] == 0:
            continue
        with open(os.path.join(policy_file_dir,str(j)+".txt"), encoding="utf8") as f:
            text = f.read()

        paragraph_extract_output = paragraph_extract(text)
        triples, tree, all_sentence = triple_extract(paragraph_extract_output)
        true_df_txt_len = true_df_txt.shape[0]
        print(triples)
        for triple in triples:
            print(triple)
        txt_tr, triple_tr, predict_len = get_acc_pre(true_df_txt, triples)





        acc = txt_tr/true_df_txt_len
        acc_result.append(acc)

        if predict_len==0:
            recall=1
        else:
            recall=triple_tr/predict_len
        rec_result.append(recall)

        all_acctrue += txt_tr
        all_rectrue += triple_tr
        all_count += true_df_txt_len
        all_precount += predict_len



        a1.append(acc)
        a2.append(recall)
        a3.append(np.mean(np.array(acc_result)))
        a4.append(np.mean(np.array(rec_result)))
        a5.append(all_acctrue/all_count)
        a6.append(all_rectrue/all_precount)


        print("%s 文件准确率 %f" % (str(j), acc))
        print("%s 文件召回率 %f" % (str(j), recall))

        score_record.write("%s 文件准确率 %f" % (str(j), acc))
        score_record.write('\n')
        score_record.write("%s 文件召回率 %f" % (str(j), recall))
        score_record.write('\n')

        print("总文件准确率 %f"%np.mean(np.array(acc_result)))
        score_record.write("总文件准确率 %f" % np.mean(np.array(acc_result)))
        score_record.write('\n')

        print("总文件召回率 %f"%np.mean(np.array(rec_result)))
        score_record.write("总文件召回率 %f" % np.mean(np.array(rec_result)))
        score_record.write('\n')

        print("all_count:%s\tall_true:%s\tprecision %f" % (all_count, all_acctrue,all_acctrue/all_count))
        score_record.write("all_count:%s\tall_true:%s\tprecision %f" % (all_count, all_acctrue, all_acctrue/all_count))
        score_record.write('\n')

        print("all_precount:%s\tall_true:%s\trecall %f" % (all_precount, all_rectrue,all_rectrue/all_precount))
        score_record.write("all_precount:%s\tall_true:%s\trecall %f" % (all_precount, all_rectrue, all_rectrue/all_precount))
        score_record.write('\n')

    score_record.close()
    pd.DataFrame({'文件准确率':a1,'文件召回率':a2,'总文件准确率':a3,'总文件召回率':a4,'allprecision':a5,'allprecount':a6}).to_csv('paperdata.csv')