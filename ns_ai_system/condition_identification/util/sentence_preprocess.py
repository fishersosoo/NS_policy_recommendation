import re
def preprocess(sentence, word):
    """预处理

    根据，。；对句子进行一个分割，找出实体所在的那个句子段，这样可以避免多个关系在同一个长句子中

    Args:
        sentence: str 原句子
        word: str 实体

    Returns:
        max_s: str 最有可能实体所在的句子
    """

    sentence = filter_sentence(sentence)
    candicate_sentence = []  # 候选的句子段
    for l1 in sentence.split('。'):
        for l2 in l1.split('；'):
            for l3 in l2.split('，'):
                candicate_sentence.append(l3)
    sim_max = 0
    sim_max_s = ''
    # 判断的逻辑为与实体字相同最多的句子为所在句子。相同多的情况下取最后一个
    for s1 in candicate_sentence:
        count = 0
        for w in word:
            if w in s1:
                count += 1
        if count > sim_max:
            sim_max = count
            sim_max_s = s1
    return sim_max_s






def filter_sentence(sentence):
    """过滤句子的无关内容

    实际上是调用各个过滤函数的主体函数

    """

    sentence = _filter_book(sentence)
    sentence = _filter_brackets(sentence)
    return sentence

def filter_punctuation(lemma, head_lemma):
    """过滤奇怪的标点符号

    把句子中的标点符号，以及一些奇怪的字符全部去掉

    Args:
        lemma：str
        head_lemma: str

    Returns:
         处理后两个新的字符串

    """
    lemma = lemma.strip()
    head_lemma = head_lemma.strip()
    # 正则表达式操作把标点符号去掉，换成空字符
    lemma = re.sub(u"[！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、`〃》"
                   u"「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。 ,;]+", "",
                   lemma)

    head_lemma = re.sub(u"[！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》"
                        u"「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。,; ]+", "", head_lemma)
    return lemma, head_lemma
def _filter_book(lemma):
    """过滤掉尖括号和尖括号之间的字符

    把字符串中的尖括号跟括号里的所有字符去掉

    Args:
        lemma:str

    Returns:
        处理后新的字符串

    """
    lemma = lemma.strip()
    lemma = re.sub(u"[<《＜].*[>》＞]", "", lemma)
    return lemma


def _filter_brackets(lemma):
    """过滤掉小括号和小括号之间的字符

    把字符串中的小括号及括号里的所有字符去掉

    Args:
        lemma：str，要处理的字符串

    Returns:
        处理后的字符串

    """
    lemma = lemma.strip()
    lemma = re.sub(u"[(（].*?[）)]", "", lemma)
    return lemma