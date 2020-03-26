import pickle
import re
import os
from sklearn.feature_extraction.text import CountVectorizer

def industryFilter(sentence):
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, 'logisticMulti')
    clfs = pickle.load(open(data_path, 'rb'))

    # 1.句子清洗
    sentencePre = preprocess(sentence)
    # 2.Count特征构造
    sentenceFeature = countFeature([sentencePre])[0]
    # 3.预测句子
    pre = predict(clfs,sentenceFeature)
    return pre

def predict(clfs,sentenceFeature):
    database = \
        {"农、林、牧、渔业": 0,
         "采矿业": 1,
         "制造业": 2,
         '电力、热力、燃气及水生产和供应业': 3,
         '建筑业': 4,
         '批发和零售业': 5,
         '交通运输、仓储和邮政业': 6,
         '住宿和餐饮业': 7,
         '信息传输、软件和信息技术服务业': 8,
         '金融业': 9,
         '房地产业': 10,
         '租赁和商务服务业': 11,
         '科学研究和技术服务业': 12,
         '水利、环境和公共设施管理业': 13,
         '居民服务、修理和其他服务业': 14,
         '卫生和社会工作': 15,
         '文化、体育和娱乐业': 16,
         '教育': 18,
         'Empty': 17
         }
    new_dict = {v: k for k, v in database.items()}

    # 模型有预测值
    pre = []
    for key in clfs:
        if clfs[key].predict(sentenceFeature) == 1:
            pre.append(new_dict[key])
    if 'Empty' in pre:
        pre = ['Empty']

    # 模型无预测值
    if len(pre)==0:
        c = 0
        k =''
        for key in clfs:
            if clfs[key].predict_proba(sentenceFeature)[0,1]>c:
                c = clfs[key].predict_proba(sentenceFeature)[0,1]
                k = key
        pre = [new_dict[k]]

    return pre


def preprocess(sentence):
        from pyhanlp import HanLP
        sentence = sentence.strip()
        # 正则表达式操作把标点符号去掉，换成空字符
        sentence = re.sub(u"[1-9]\.", "", sentence)
        sentence = re.sub(u"[1-9]、", "", sentence)
        sentence = re.sub(u"[①②③④⑤⑥⑦⑧⑨⑩]", "", sentence)
        sentence = re.sub(u"[<《＜].*[>》＞]", "", sentence)
        sentence = re.sub(u"[(（].*?[）)]", "", sentence)
        sentence = re.sub(u"[0-9].*?[）)]", "", sentence)
        sentence = re.sub(u"[！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、`〃》"
                       u"「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。 ,;]+", "",
                       sentence)
        sentence = ' '.join([term.word for term in HanLP.segment(sentence)])
        return sentence
def countFeature(xtrain):
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, 'ctv')
    vocabulary = pickle.load(open(data_path, 'rb'))
    loaded_vec = CountVectorizer(decode_error="replace", vocabulary=vocabulary)
    xtrain_ctv = loaded_vec.transform(xtrain)
    return xtrain_ctv

if __name__ == "__main__":
    sentences = ['2.申报项目具有近三年授权的发明专利（授权公告日期在2015年1月1日至2017年12月31日之间）0',
                 "（4）经我区认定的杰出人才、优秀人才、青年后备人才创办的企业。1",
                 "（二）申请认定高端领军人才B证，须符合须符合《实施细则》第十三条第（二）项所列长期创新条件；,1",
                 "3.申报单位于2017年度向非关联企业提供科技研发、检验检测、成果转化、科技咨询等科技服务。,0"]
    print(industryFilter(sentences))
