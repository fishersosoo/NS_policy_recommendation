from collections import namedtuple
import os

word_entity = namedtuple('word_entity', ['order','word','category','len','ordercount'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S','P','O'])
syntax_tuple = namedtuple('syntax_tuple',['LEMMA','DEPREL','HEADLEMMA'])

class TupleExtracter:
    def __init__(self):
        pass

    def complete_tuple(self,word,syntaxtuple):
        add_word = [""]
        for tuple in syntaxtuple:
            if tuple.HEADLEMMA == word and tuple.DEPREL == "定中关系":
                add_word.append(tuple.LEMMA)
            if tuple.HEADLEMMA == word and tuple.DEPREL == "状中结构" :
                add_word[0] = tuple.LEMMA
        last_word = ""
        for oneword in add_word:
            last_word = last_word + oneword
        last_word = last_word + word
        #print(last_word)
        return last_word

    #对主谓宾结构三元组进行过滤补充
    def tuple_fillter_svo(self,syntaxtuple,recognizedentity,spotuple):
        tuple_s = spotuple.S
        tuple_p = spotuple.P
        tuple_o = spotuple.O
        #print(spotuple)
        category = []
        norm = []
        qualification =[]
        number = []

        for ents in recognizedentity:
            if ents.category == "norm":
                norm.append(ents.word)
            elif ents.category == "category":
                category.append(ents.word)
            elif ents.category == "qualification":
                qualification.append(ents.word)
            elif ents.category == "number":
                number.append(ents.word)

        res_tuple = None

        #主语为指标名
        if tuple_s in norm and tuple_o != None :
            if "元" in tuple_o :
                res_tuple =  three_tuple_entity(S=tuple_s, P=self.complete_tuple(tuple_p,syntaxtuple), O=self.complete_tuple(tuple_o,syntaxtuple))
            if "以上" in tuple_o :
                res_tuple =  three_tuple_entity(S=tuple_s, P=tuple_p, O=self.complete_tuple(tuple_o,syntaxtuple))

        #宾语为资格名、类型名
        elif tuple_o in qualification or tuple_o in category:
            res_tuple = spotuple

        return res_tuple

    #对单个句子进行三元组抽取
    def predicate_extraction(self,syntaxtuple,recognizedentity):

        #处理主谓宾结构
        keyword = ""
        for word in syntaxtuple:
            if word.DEPREL == "核心关系" :
                keyword = word.LEMMA

        s_array = []
        o_array = []

        for word in syntaxtuple:
            if word.DEPREL == "主谓关系" and word.HEADLEMMA == keyword:
                s_array.append(word.LEMMA)
            elif word.DEPREL == "动宾关系" and word.HEADLEMMA == keyword:
                o_array.append(word.LEMMA)
            elif word.DEPREL == "介宾关系" and word.HEADLEMMA == keyword:
                o_array.append(word.LEMMA)

        if len(s_array) == 0:
            s_array.append("NONE")

        if len(o_array) == 0:
            o_array.append("NONE")


        if o_array[0] == "NONE" and s_array[0] == "NONE":
            return
        res_tuple = self.tuple_fillter_svo(syntaxtuple,recognizedentity,three_tuple_entity(S=s_array[0], P=keyword, O=o_array[0]))
        return res_tuple

if __name__=="__main__":
    syntaxtuple = [syntax_tuple(LEMMA='上一', DEPREL='定中关系', HEADLEMMA='年度'), syntax_tuple(LEMMA='年度', DEPREL='定中关系', HEADLEMMA='纳税总额'),
     syntax_tuple(LEMMA='在', DEPREL='定中关系', HEADLEMMA='纳税总额'), syntax_tuple(LEMMA='我', DEPREL='定中关系', HEADLEMMA='区'),
     syntax_tuple(LEMMA='区', DEPREL='介宾关系', HEADLEMMA='在'), syntax_tuple(LEMMA='纳税总额', DEPREL='主谓关系', HEADLEMMA='低于'),
     syntax_tuple(LEMMA='不', DEPREL='状中结构', HEADLEMMA='低于'),
     syntax_tuple(LEMMA='低于', DEPREL='核心关系', HEADLEMMA='##核心##'),
     syntax_tuple(LEMMA='1000', DEPREL='定中关系', HEADLEMMA='万元'), syntax_tuple(LEMMA='万元', DEPREL='动宾关系', HEADLEMMA='低于'),
     syntax_tuple(LEMMA='。', DEPREL='标点符号', HEADLEMMA='低于')]
    recognizedentity=entity = [word_entity(order='16', word='纳税总额', category='norm'), word_entity(order='17|18', word='1亿元', category='number')]

    tupleextract = TupleExtracter()
    res = tupleextract.predicate_extraction(syntaxtuple,recognizedentity)
    print(res)
