import pickle
import re
from pyhanlp import *
from sklearn.feature_extraction.text import CountVectorizer
def talentFilter(sentence):
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, 'logisticClassify')
    clf = pickle.load(open(data_path, 'rb'))

    # 1.句子清洗
    sentencePre = preprocess(sentence)
    # 2.Count特征构造
    sentenceFeature = countFeature([sentencePre])
    for sf in sentenceFeature:
        predictions = clf.predict(sf)
        if predictions == 0:
            return False
        else:
            return True

def preprocess(sentence):
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
    print(talentFilter(sentences))
