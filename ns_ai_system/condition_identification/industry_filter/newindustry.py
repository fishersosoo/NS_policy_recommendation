import os
from condition_identification.args import INDUSTRY_LIST
from condition_identification.util.string_process import *
from data_management.api.industry_standard import *
def industryFilter(document):
    result = titleFilter(document)
    result.extend(contentFileter(document))
    result=nameProcess(result)
    result = list(set(result))
    result=relationProcess(result)
    return result


def titleFilter(document):
    print('title')
    result = []
    similarWord = []
    title = document.title
    for label in INDUSTRY_LIST:
        category_nouns = get_industry_standard(label)
        nouns = getNouns(label)
        if 'children' in category_nouns:
            for children in category_nouns['children']:
                nouns.extend([children['label']])
                if 'children' in children:
                    nouns.extend([x['label'] for x in children['children']])
        for noun in nouns:
            if noun in title:
                result.append(label)
                similarWord.append(noun)
    print(similarWord)
    return result

def contentFileter(document):
    print('content')
    # data没有取名词的操作
    result = []
    similarWord = []
    text = document.content
    for label in INDUSTRY_LIST:
        category_nouns = get_industry_standard(label)
        nouns =[label]
        if 'children' in category_nouns:
            for children in category_nouns['children']:
                nouns.extend([children['label']])
                if 'children' in children:
                    nouns.extend([x['label'] for x in children['children']])
        for noun in nouns:
            if noun in text:
                result.append(label)
                similarWord.append(noun)
    print(similarWord)
    return result

# def similarFilter(document):
#     print('similar')
#     result_scores = {}
#     result=[]
#     similarWord=[]
#     import pickle
#     basepath = os.path.abspath(__file__)
#     folder = os.path.dirname(basepath)
#     data_path = os.path.join(folder, 'scores')
#     f = open(data_path, 'rb')
#     category_nouns = pickle.load(f)
#
#     text = document.content
#     for key in category_nouns:
#         score = 0
#         value = category_nouns[key]
#         for vk in value:
#             if vk in text:
#                 score+=value[vk]
#                 similarWord.append(vk)
#         if score ==1 :
#             score=0
#         result_scores[key] = score
#     list1 = sorted(result_scores.items(), key=lambda x: x[1], reverse=True)
#     for rs in list1:
#         if rs[1]>0.1:
#             result.append(rs[0])
#     print(similarWord)
#     return result

def nameProcess(result):
    i=0
    while i <len(result):
        if result[i] == '农业、林业、牧业、渔业':
            result[i] = '农、林、牧、渔业'
        i+=1
    return result
def relationProcess(result):
    if '农、林、牧、渔业' in result and len(result)>1:
        result.remove('农、林、牧、渔业')
    return result
