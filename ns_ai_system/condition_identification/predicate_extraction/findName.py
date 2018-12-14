import re
from collections import namedtuple

from treelib import Tree

from condition_identification.dict_management.dict_manage import EntityDict
from condition_identification.entity_link.entity_recognizer import EntityRecognizer
from condition_identification.predicate_extraction.tuple_extracter import TupleExtracter
from condition_identification.syntax_analysis.sentence_analysis import HanlpSynataxAnalysis
from condition_identification.word_segmentation.jieba_segmentation import Segmentation
from condition_identification.bonus_identify.DocTree import DocTree
from pyhanlp import *

word_entity = namedtuple('word_entity', ['order', 'word', 'category', 'len', 'ordercount'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S', 'P', 'O'])
syntax_tuple = namedtuple('syntax_tuple', ['LEMMA', 'DEPREL', 'HEADLEMMA', 'POSTAG', 'HEAD'])

class FindName():
    def __init__(self):
        pass

    def get_linked_word(self,wordid,word,idwords,idpostag):
        linked_words = []
        curword = word
        if idpostag[wordid] == "n" or idpostag[wordid] == "vn":
            flag = True
            curid = wordid-1
            try:
                while idpostag[curid] == "n" or idpostag[curid] == "vn":
                    linked_words.append(str(idwords[curid]+curword))
                    curid = curid-1
            except Exception as e:
                pass

        return linked_words
    def get_maybe_norm(self,sentence):
        norms = []
        sentence_dependency_res = HanLP.parseDependency(sentence)
        analysisres = sentence_dependency_res.getWordArray()
        idword = {}
        idpostag = {}
        for word in analysisres:
            idword[word.ID] = word.LEMMA
            idpostag[word.ID] = word.POSTAG

        for word in analysisres:
            #print("%s --%s--> %s--> %s--> %s" % (word.LEMMA, word.DEPREL, word.HEAD.LEMMA, word.POSTAG,word.CPOSTAG))
            if  word.DEPREL == "动宾关系" or word.DEPREL == "主谓关系":
                norms.append(word.LEMMA)
                norms = norms+ self.get_linked_word(word.ID,word.LEMMA,idword,idpostag)
        return norms

    def find_names_by_file(self,filepath):
        tree = DocTree()
        tree.construct(filepath, 1)
        st = tree.get_bonus_tree()

        sentences = []
        sentences_dict = {}
        for node in st.all_nodes():
            if node.identifier == "partition" or node.identifier == "root":
                continue
            sentence = node.tag
            sentences_dict[sentence] = self.get_maybe_norm(sentence)

        print(sentences_dict)
        return sentences_dict

    def find_names_by_str(self, filetext):
        tree = DocTree()
        tree.construct(filetext, 2)
        st = tree.get_bonus_tree()

        sentences = []
        sentences_dict = {}
        for node in st.all_nodes():
            if node.identifier == "partition" or node.identifier == "root":
                continue
            sentence = node.tag
            sentences_dict[sentence] = self.get_maybe_norm(sentence)

        print(sentences_dict)
        return sentences_dict

if __name__ == "__main__":
    fn = FindName()
    fn.find_names_by_file(r'C:\Users\edward\Desktop\指南们\26.txt')
