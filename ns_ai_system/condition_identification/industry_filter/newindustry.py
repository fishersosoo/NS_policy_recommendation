import os
import pickle
from condition_identification.util.string_process import *
def industryFilter(document):
    print('industryFilter')
    result = titleFilter(document)
    result.extend(contentFileter(document))
    # if len(result)==0:
    #     result.extend(similarFilter(document))
    result=nameProcess(result)
    result = list(set(result))
    if '农、林、牧、渔业' in result:
        result.remove('农、林、牧、渔业')
    if '居民服务、修理和其他服务业' in result:
        result.remove('居民服务、修理和其他服务业')
    if '房地产业' in result:
        result.remove('房地产业')
    if '水利、环境和公共设施管理业' in result:
        result.remove('水利、环境和公共设施管理业')
    return result


def titleFilter(document):
    print('title')
    result = []
    similarWord = []
    import pickle
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, 'origin_data')
    f = open(data_path, 'rb')
    category_nouns = pickle.load(f)
    title = document.title
    for key in category_nouns:
        nouns = [key]
        nouns.extend(category_nouns[key])
        for noun in nouns:
            if noun in title:
                result.append(key)
                similarWord.append(noun)
    print(similarWord)
    return result

def contentFileter(document):
    print('content')
    # data没有取名词的操作
    result = []
    similarWord = []
    import pickle
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, 'origin_data')
    f = open(data_path, 'rb')
    category_nouns = pickle.load(f)
    text = document.content
    for key in category_nouns:
        nouns = getNouns(key)
        nouns.extend(category_nouns[key])
        for noun in nouns:
            if noun in text:
                result.append(key)
                similarWord.append(noun)
    print(similarWord)
    return result

def similarFilter(document):
    print('similar')
    result_scores = {}
    result=[]
    similarWord=[]
    import pickle
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, 'scores')
    f = open(data_path, 'rb')
    category_nouns = pickle.load(f)

    text = document.content
    for key in category_nouns:
        score = 0
        value = category_nouns[key]
        for vk in value:
            if vk in text:
                score+=value[vk]
                similarWord.append(vk)
        if score ==1 :
            score=0
        result_scores[key] = score
    list1 = sorted(result_scores.items(), key=lambda x: x[1], reverse=True)
    for rs in list1:
        if rs[1]>0.1:
            result.append(rs[0])
    print(similarWord)
    return result

def nameProcess(result):
    i=0
    while i <len(result):
        if result[i] == '农业、林业、牧业、渔业':
            result[i] = '农、林、牧、渔业'
        if result[i] == '卫生和社会工作':
            result[i] = ''
        i+=1
    return result
