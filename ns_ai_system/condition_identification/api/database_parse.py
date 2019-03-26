from name_entity_recognition.extract import *
import os
def database_extract(lines,outputname,max_length=-1,len_threshold=1):
    '''
    数据库的列值进行抽取,抽取后以文本的形式放在name_entity_recognition下的evalue文件夹中
    :param lines: 传过来的数据库的列值
    :param outputname: 数据库的列名
    :param len_threshold: 分词的粒度，一般不用修改
    :param max_length: 为了节省时间，可以选择只抽前Man_length条
    :return:
    '''
    count = 0
    file_path = os.path.dirname(__file__)
    file_path += '/../name_entity_recognition/evalue/'
    file_path+=outputname

    f = open(file_path, 'w', encoding='utf8')
    f.close()
    resultword=[]
    for line in lines:
        count+=1
        if max_length!=-1:
            if count>max_length:
                break
        resultword.extend(extract_keyword(line, len_threshold))
    database_cluster(resultword, file_path)



def database_cluster(lines,outputname):
    '''
    对列数据很多的列进行聚类，从而剔除无关值
    :param lines: 传过来的数据库的列值
    :param outputname: 数据库的列名
    :return:
    '''
    from bert_serving.client import BertClient
    bc = BertClient()

    import pandas as pd
    import numpy as np
    from tqdm import tqdm
    tqdm.pandas()

    vs = set()
    vec_dict = {}
    for line in tqdm(lines):
        line = line.strip()
        vec_dict[line] = bc.encode([line])
        vs.add(line)
    vs = list(vs)
    # 如果数据太少就没有清除的必要
    if len(vs)<300:
        with open(outputname, 'w', encoding='utf8')as wf:
            for i in range(len(vs)):
                wf.write(vs[i])
                wf.write('\n')


    else:
        result_csv = pd.DataFrame({'filed': np.array(vs), 'count': np.zeros(len(vs))})
        diff = 0
        for key in tqdm(vs):
            value_csv = pd.DataFrame({'filed': np.array(vs), 'value': np.zeros(len(vs))})
            diff += 1
            for j in range(diff, len(vs)):
                key2 = vs[j]
                value_csv.loc[value_csv['filed'] == key2, 'value'] = cos_sim(vec_dict[key], vec_dict[key2])
            value_csv = value_csv[value_csv['value'] > 0.9]
            value_csv = value_csv['filed'].values
            for i in range(value_csv.shape[0]):
                result_csv.loc[result_csv['filed'] == value_csv[i], 'count'] += 1
        result_csv=result_csv[result_csv['count']>result_csv['count'].quantile(0.4)]


        with open(outputname, 'w', encoding='utf8')as wf:
            result_csv=result_csv['filed'].values
            for i in range(len(result_csv)):
                wf.write(result_csv[i])
                wf.write('\n')
# TODO 还少一个接口可以修改arg.py
if __name__=='__main__':
    words=['1']*1000
    # with open('F:\\txt\\txt\\2.txt','r',encoding='utf8')as rf:
    #     for line in rf:
    #         words.append(line.strip())
    database_extract(words,'21.txt',10)
