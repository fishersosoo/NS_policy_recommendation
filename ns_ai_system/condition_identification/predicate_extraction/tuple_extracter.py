from collections import namedtuple
import os

word_entity = namedtuple('word_entity', ['order','word','category','len','ordercount'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S','P','O'])
syntax_tuple = namedtuple('syntax_tuple',['LEMMA','DEPREL','HEADLEMMA','POSTAG','HEAD'])

class TupleExtracter:
    def __init__(self):
        pass

    def complete_tuple(self,word,syntaxtuple):
        # add_word = [""]
        # for tuple in syntaxdict:
        #     if tuple.HEADLEMMA == word and tuple.DEPREL == "定中关系":
        #         add_word.append(tuple.LEMMA)
        #     if tuple.HEADLEMMA == word and tuple.DEPREL == "状中结构" :
        #         add_word[0] = tuple.LEMMA
        # last_word = ""
        # for oneword in add_word:
        #     last_word = last_word + oneword
        # last_word = last_word + word
        # #print(last_word)
        # return last_word
        #print("completetuple"+word)

        for tuple in syntaxtuple:
            if tuple.HEADLEMMA == word and (tuple.DEPREL == "定中关系"or tuple.DEPREL == "前置宾语"):
                addword = tuple.LEMMA
                word = self.complete_tuple(addword,syntaxtuple)+word
            elif tuple.HEADLEMMA == word and tuple.DEPREL == "并列关系":
                addword = tuple.LEMMA
                word = word+self.complete_tuple(addword,syntaxtuple)+word
            else:
                continue
        return word
        # if word in syntaxdict.keys():
        #     if '定中关系' in syntaxdict[word].keys():
        #         addword = syntaxdict[word]['定中关系']
        #         word =self.complete_tuple(addword,syntaxdict)+ word
        #     else:
        #         return word
        # else:
        #     return word
        # return word

    #对主谓宾结构三元组进行过滤补充
    def tuple_fillter_svo(self,syntaxtuple,recognizedentity,spotuple):
        tuple_s = spotuple.S
        tuple_p = spotuple.P
        tuple_o = spotuple.O
        # #print(spotuple)
        # category = []
        # norm = []
        # qualification =[]
        # number = []
        # print(recognizedentity)
        # for ents in recognizedentity:
        #     if ents.category == "norm":
        #         norm.append(ents.word)
        #     elif ents.category == "category":
        #         category.append(ents.word)
        #     elif ents.category == "qualification":
        #         qualification.append(ents.word)
        #     elif ents.category == "number":
        #         number.append(ents.word)
        #
        # res_tuple = spotuple
        # #res_tuple = None
        # #主语为指标名
        # if tuple_s in norm and tuple_o != None :
        #     if "元" in tuple_o :
        #         res_tuple =  three_tuple_entity(S=tuple_s, P=self.complete_tuple(tuple_p,syntaxtuple), O=self.complete_tuple(tuple_o,syntaxtuple))
        #     if "以上" in tuple_o :
        #         res_tuple =  three_tuple_entity(S=tuple_s, P=tuple_p, O=self.complete_tuple(tuple_o,syntaxtuple))
        #
        # #宾语为资格名、类型名
        # elif tuple_o in qualification or tuple_o in category:
        #     res_tuple = spotuple
        # else:
        #     res_tuple = three_tuple_entity(S=self.complete_tuple(tuple_s, syntaxtuple), P=tuple_p, O=self.complete_tuple(tuple_o, syntaxtuple))

        tuple_s = self.complete_tuple(tuple_s, syntaxtuple)
        tuple_o = self.complete_tuple(tuple_o, syntaxtuple)
        s = {}
        p = {}
        o = {}
        s["tag"] = tuple_s
        p["tag"] = tuple_p
        o["tag"] = tuple_o
        res_tuple = three_tuple_entity(S=s, P=p,O=o)
        return res_tuple

    #对单个句子进行三元组抽取
    def predicate_extraction(self,syntaxtuple,recognizedentity):
        res_tuples = []
        # 处理主谓宾结构
        syntax_dict = {}

        keywords = []
        for word in syntaxtuple:
            if word.DEPREL == "核心关系":
                keywords.append(word.LEMMA)

        #syntaxdict_dict = {}
        for word in syntaxtuple:

            try:
                if str(word.DEPREL).strip() == "主谓关系" or str(word.DEPREL).strip() == "动宾关系"or str(word.DEPREL).strip() == "介宾关系"or str(word.DEPREL).strip() == "动补结构":
                    syntaxdict_dict = {}

                    if str(word.HEAD.LEMMA) in syntax_dict.keys():
                        if str(word.DEPREL) in syntax_dict[str(word.HEAD.LEMMA)].keys():
                            syntax_dict[str(word.HEAD.LEMMA)][str(word.DEPREL)] = str(syntax_dict[str(word.HEAD.LEMMA)][str(word.DEPREL)])\
                                                                                  +str(word.LEMMA)
                        else:
                            syntax_dict[str(word.HEAD.LEMMA)][str(word.DEPREL)] = str(word.LEMMA)
                    else:
                        syntaxdict_dict[str(word.DEPREL)] = str(word.LEMMA)
                        syntax_dict[str(word.HEAD.LEMMA)] = syntaxdict_dict
                    #print(syntax_dict)

            except:
                print("predicate_extraction error")
        # print(syntax_dict)

        for key in syntax_dict:
            s = ""
            o = ""
            if key in keywords:
                if "主谓关系" in syntax_dict[key].keys() or "动宾关系" in syntax_dict[key].keys() \
                        or "介宾关系" in syntax_dict[key].keys()or "动补结构" in syntax_dict[key].keys():

                    try:
                        s = syntax_dict[key]['主谓关系']
                    except:
                        pass
                        #print("没有主谓关系")

                    try:
                        o = syntax_dict[key]['动宾关系']
                        if o in syntax_dict.keys():
                            if '主谓关系' in syntax_dict[o].keys():
                                o = o + syntax_dict[o]['主谓关系']
                    except:
                        pass
                        #print("没有动宾关系")
                    try:
                        o = syntax_dict[key]['介宾关系']
                    except:
                        pass
                        #print("没有动宾关系")

                    try:
                        dongbu = syntax_dict[key]['动补结构']
                        o = syntax_dict[dongbu]['介宾关系']
                        key = key + dongbu
                    except:
                        pass
                        #print("没有动宾关系")

                    res_tuple = self.tuple_fillter_svo(syntaxtuple, recognizedentity,
                                                       three_tuple_entity(S=s, P=key, O=o))
                    res_tuples.append(res_tuple)

        return res_tuples
        #
        # keywords = []
        # for word in syntaxtuple:
        #     if word.DEPREL == "核心关系" or word.POSTAG=="v" :
        #         #print (word.POSTAG)
        #         keywords.append(word.LEMMA)
        #
        # for keyword in keywords:
        #     s_array = []
        #     o_array = []
        #
        #     for word in syntaxtuple:
        #         if word.DEPREL == "主谓关系" and word.HEADLEMMA == keyword:
        #             s_array.append(word.LEMMA)
        #         elif word.DEPREL == "动宾关系" and word.HEADLEMMA == keyword:
        #             o_array.append(word.LEMMA)
        #         elif word.DEPREL == "介宾关系" and word.HEADLEMMA == keyword:
        #             o_array.append(word.LEMMA)
        #
        #     if len(s_array) == 0:
        #         s_array.append("NONE")
        #
        #     if len(o_array) == 0:
        #         o_array.append("NONE")
        #
        #
        #     if o_array[0] == "NONE" and s_array[0] == "NONE":
        #         return
        #     res_tuple = self.tuple_fillter_svo(syntaxtuple,recognizedentity,three_tuple_entity(S=s_array[0], P=keyword, O=o_array[0]))
        #     res_tuples.append(res_tuple)
        # return res_tuples

if __name__=="__main__":
    syntaxtuple = [syntax_tuple(LEMMA='1.', DEPREL='状中结构', HEADLEMMA='对'), syntax_tuple(LEMMA='对', DEPREL='核心关系', HEADLEMMA='##核心##'), syntax_tuple(LEMMA='内资企业', DEPREL='介宾关系', HEADLEMMA='对')]
    recognizedentity=entity = [word_entity(order='16', word='内资企业', category='category',len='1',ordercount='1'), word_entity(order='17|18', word='1亿元', category='number',len='1',ordercount='1')]

    tupleextract = TupleExtracter()
    res = tupleextract.predicate_extraction(syntaxtuple,recognizedentity)
    print(res)
