# coding=utf-8
from collections import namedtuple

word_entity = namedtuple('word_entity', ['order', 'word', 'category', 'len', 'ordercount'])


class EntityRecognizer:
    def __init__(self):
        pass

    def entity_mark(self, sentence, entity_set):  # sentence为分词后的句子，以元组形式传入
        # print(sentence)
        word_entitys = []
        money_rep = ["万元", "亿元", "千元", "元", "百元"]
        curlen = 0
        for i, wordpair in enumerate(sentence):
            # 判断是否资格、类型实体
            word = wordpair.word
            for entity in entity_set:
                if word == entity.name:
                    word_entitys.append(
                        word_entity(order=str(i), word=word, category=entity.category, len=curlen, ordercount=1))
            # 判断是否值
            if word.isdigit():
                if i + 1 < len(sentence):
                    if sentence[i + 1].word in money_rep:
                        # orders=[]
                        # orders.append(str(i))
                        # orders.append(str(i+1))
                        word_entitys.append(
                            word_entity(order=str(i), word=word + sentence[i + 1].word, category="number", len=curlen,
                                        ordercount=2))
            curlen = curlen + len(word)
        return word_entitys


if __name__ == "__main__":
    entity = namedtuple('entity', ['name', 'category'])
    entity_set = (
    entity(name='营业收入', category='norm'), entity(name='纳税总额', category='norm'), entity(name='注册资本', category='norm'),
    entity(name='外资企业', category='category'), entity(name='外国非企业经济组织代表机构', category='category'),
    entity(name='内资企业', category='category'), entity(name='独立法人资格', category='qualification'),
    entity(name='世界1000强企业', category='qualification'), entity(name='中央大型企业', category='qualification'),
    entity(name='中国企业500强', category='qualification'), entity(name='中国民营企业500强', category='qualification'),
    entity(name='跨国公司', category='qualification'), entity(name='世界1000强', category='qualification'))
    entityRecognizer = EntityRecognizer()
    sentence = (
    '1', '.', '属于', '世界1000强企业', '、', '中央大型企业', '、', '中国企业500强', '、', '中国民营企业500强', '、', '商务部', '认定', '或', '备案', '的',
    '跨国公司', '1000', '万元')
    # print(entityRecognizer.entity_mark(sentence,entity_set))
