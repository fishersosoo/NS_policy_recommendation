import re
import sys

sys.path.append("..")
from dict_management.dict_management import EntityDict
from word_segmentation.jieba_segmentation import Segmentation
from entity_link.entity_recognizer import EntityRecognizer
from syntax_analysis.sentence_analysis import HanlpSynataxAnalysis
from predicate_extraction.tuple_extracter import TupleExtracter

from collections import namedtuple
from os import path
from treelib import Tree

word_entity = namedtuple('word_entity', ['order', 'word', 'category', 'len', 'ordercount'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S', 'P', 'O'])
syntax_tuple = namedtuple('syntax_tuple', ['LEMMA', 'DEPREL', 'HEADLEMMA'])


class TupleBonus:
    def __init__(self, dict_dir=None):

        self.segmentation = Segmentation()
        self.entity_set = EntityDict()
        self.entityrecognizer = EntityRecognizer()
        self.hanlpanalysis = HanlpSynataxAnalysis()
        self.extracter = TupleExtracter()
        self.bonus_tree = Tree()

        self.segementation_construct(dict_dir=dict_dir)
        # print(self.entity_set.entity_word)

    def segementation_construct(self, dict_dir=None):
        # load dict
        if dict_dir is not None:
            self.entity_set.load_dict(path.join(dict_dir, "norm_dict"), "norm")
            self.entity_set.load_dict(path.join(dict_dir, "category_dict"), "category")
            self.entity_set.load_dict(path.join(dict_dir, "qualification_dict"), "qualification")
        else:
            self.entity_set.load_dict(
                r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\norm_dict', "norm")
            self.entity_set.load_dict(
                r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\category_dict',
                "category")
            self.entity_set.load_dict(
                r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\qualification_dict',
                "qualification")
        # print(entity_set.entity_set)
        for entity in self.entity_set.entity_word:
            print(entity)
            self.segmentation.tokenizer.add_word(entity, 1000)

    def entity_recognize(self, sentence):
        words_sentence = self.segmentation.psegcut(sentence)
        # print(words_sentence)
        result = self.entityrecognizer.entity_mark(tuple(words_sentence), self.entity_set.entity_set)
        return result

    def tuple_extract(self, sentence):
        entities = self.entity_recognize(sentence)
        split_sentence = re.split("[;；。,，：:]", sentence)
        spo_arrays = []
        for one_sentence in split_sentence:
            if len(one_sentence) == 0:
                continue
            syntaxtuple = self.hanlpanalysis.parseDependency(one_sentence)
            spo_tuple = self.extracter.predicate_extraction(syntaxtuple, entities)
            if spo_tuple != None:
                spo_arrays.append(spo_tuple)
        return spo_arrays

    def bonus_tuple_analysis(self, doctree):
        pytree = doctree.get_tree()
        bonuslist = doctree.get_bonus_nodes()
        leaves = pytree.leaves()

        self.bonus_tree.create_node("BONUS_ROOT", "root")

        tagnumber = 1
        for bonus in bonuslist:
            bonus_content = pytree.get_node(bonus).data[0]
            self.bonus_tree.create_node(bonus_content, str(tagnumber), parent="root")
            subtree = Tree(pytree.subtree(bonus), deep=True)
            self.analysis_single_bonus(bonus_content, subtree, str(tagnumber))
            # print('\n')
            tagnumber = tagnumber + 1
        # self.bonus_tree.show()

    def analysis_single_bonus(self, bonus, subtree, tagnumber):

        treedepth = subtree.depth()
        if treedepth == 0:
            k = 0
            if len(subtree.leaves()[0].data) > 1:
                k = 1
            rootsentence = subtree.leaves()[0].data[k]
            self.bonus_tree.create_node("AND", bonus, parent=tagnumber)
            for onetuple in self.tuple_extract(rootsentence):
                if onetuple is not None:
                    self.bonus_tree.create_node(str(tuple(onetuple)), parent=bonus)
            return

        self.bonus_tree.create_node("OR", bonus, parent=tagnumber)
        allnodes = subtree.leaves()
        # print(allnodes)
        for node in allnodes:
            k = 0
            if len(node.data) > 1:
                k = 1
            sentence = node.data[k]
            nodedepth = subtree.depth(node)
            for spo in self.tuple_extract(sentence):
                if spo is not None:
                    self.bonus_tree.create_node(str(tuple(spo)), parent=bonus)

    def get_bonus_tree(self):
        return self.bonus_tree


if __name__ == "__main__":
    tree = Tree()
