import re
import sys

sys.path.append("..")
from dict_management.dict_manage import EntityDict
from word_segmentation.jieba_segmentation import Segmentation
from entity_link.entity_recognizer import EntityRecognizer
from syntax_analysis.sentence_analysis import HanlpSynataxAnalysis
from predicate_extraction.tuple_extracter import TupleExtracter

from collections import namedtuple
from os import path
from treelib import Tree

word_entity = namedtuple('word_entity', ['order', 'word', 'category', 'len', 'ordercount'])
three_tuple_entity = namedtuple('three_tuple_entity', ['S', 'P', 'O'])
syntax_tuple = namedtuple('syntax_tuple', ['LEMMA', 'DEPREL', 'HEADLEMMA', 'POSTAG', 'HEAD'])


class Bonus_Condition_Tree(Tree):
    def __init__(self):
        super().__init__()

    def get_all_bonus(self):
        bonus = []
        bonus_node = self.children("root")
        for single_bonus in bonus_node:
            bonus.append(single_bonus.tag)
        return bonus

    def get_node_type(self, node):
        return node.data['TYPE']

    def get_node_content(self, node):
        return node.data['CONTENT']

    def get_node_data(self, node):
        return node.data


class TupleBonus:
    def __init__(self, dict_dir=None, if_edit_hanlpdict=1):

        self.segmentation = Segmentation()
        self.entity_set = EntityDict()
        self.entityrecognizer = EntityRecognizer()
        self.hanlpanalysis = HanlpSynataxAnalysis()
        self.extracter = TupleExtracter()
        self.bonus_tree = Bonus_Condition_Tree()

        # self.segementation_construct(dict_dir=dict_dir)
        # if if_edit_hanlpdict == 1 and dict_dir != None:
        #     self.hanlpanalysis.reloadHanlpCustomDictionary(dict_dir)
        # print(self.entity_set.entity_word)

    # def segementation_construct(self, dict_dir=None):
    #     # load dict
    #     if dict_dir is not None:
    #         self.entity_set.load_dict(path.join(dict_dir, "norm_dict"), "norm")
    #         self.entity_set.load_dict(path.join(dict_dir, "category_dict"), "category")
    #         self.entity_set.load_dict(path.join(dict_dir, "qualification_dict"), "qualification")
    #     else:
    #         self.entity_set.load_dict(
    #             r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\norm_dict', "norm")
    #         self.entity_set.load_dict(
    #             r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\category_dict',
    #             "category")
    #         self.entity_set.load_dict(
    #             r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\qualification_dict',
    #             "qualification")
    #     # print(entity_set.entity_set)
    #     for entity in self.entity_set.entity_word:
    #         # print(entity)
    #         self.segmentation.tokenizer.add_word(entity, 1000)

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
                spo_arrays = spo_arrays + spo_tuple
        return spo_arrays

    def get_node_data_dic(self, type, content):
        data_dic = {'TYPE': '', 'CONTENT': ''}
        data_dic["TYPE"] = type
        data_dic["CONTENT"] = content
        return data_dic

    def get_all_bonus_content(self, bonusnode, pytree):
        bonus_content = ""
        tree_path = tuple(pytree.rsearch(bonusnode))
        length = len(tree_path)
        for i, node in enumerate(tree_path):
            if i + 1 < length:
                content = pytree.get_node(node).tag[0]
                bonus_content = content + " " + bonus_content
        return bonus_content
        print(bonus_content)

    def get_all_bonus_list(self, t):
        # count = 0
        # bonus_list = []
        # while t.get_node('c' + 'root' + str(count)):
        #     node = t.parent('c' + 'root' + str(count))
        #     bonus_list.append(node.identifier)
        #     count += 1
        node = t.all_nodes()[0]

        bonus_list = []
        bonus_list.append(node.identifier)
        return bonus_list

    def bonus_tuple_analysis(self, doctree):
        pytree = doctree
        bonuslist = self.get_all_bonus_list(doctree)

        self.bonus_tree.create_node(tag="BONUS_ROOT", identifier="root", data=self.get_node_data_dic("ROOT", "None"))

        tagnumber = 1

        for bonus in bonuslist:

            #all_bonus_content = self.get_all_bonus_content(bonus, pytree)
            bonus_content = pytree.get_node(bonus).tag

            bonus_node = self.bonus_tree.create_node(tag=bonus_content, identifier=str(tagnumber), parent="root",
                                                     data=self.get_node_data_dic("BONUS", bonus_content))

            # 构建每个优惠的条件节点树
            bonus_childrens = pytree.children(bonus)
            if len(bonus_childrens) == 0:
                continue
            subtree = Tree(pytree.subtree(bonus_childrens[0].identifier), deep=True)
            flag = self.analysis_single_bonus(bonus_content, subtree, str(tagnumber))

            flag = True
            if flag == False:
                self.bonus_tree.remove_subtree(str(tagnumber))
            # print('\n')
            tagnumber = tagnumber + 1
        # self.bonus_tree.show()

    def analysis_single_bonus(self, bonus, subtree, tagnumber):
        # print("subtree:")
        # print(subtree)
        flag = False

        path_list = subtree.paths_to_leaves()

        if len(path_list) > 0:
            pass
        else:
            return flag

        logictag = "and" + str(tagnumber)
        self.bonus_tree.create_node("AND", identifier=logictag, parent=tagnumber,
                                    data=self.get_node_data_dic("LOGIC", "AND"))
        print(path_list)

        for i, idlist in enumerate(path_list):

            if i == 0:
                continue
            id = idlist[1]
            sentence = subtree.get_node(id).tag
            print(sentence)
            for spo in self.tuple_extract(sentence):
                if spo is not None:
                    flag = True
                    self.bonus_tree.create_node(tag=str(tuple(spo)), parent=logictag,
                                                data=self.get_node_data_dic("CONDITION", str(tuple(spo))))

        print("\n")
        return flag

    def get_bonus_tree(self):
        return self.bonus_tree


if __name__ == "__main__":
    tuple_bonus = TupleBonus()

    sentence2 = '对在南沙港区完成年度外贸集装箱吞吐量达到10万TEU的新落户船公司给予250万元的一次性奖励'
    try:
        res = tuple_bonus.tuple_extract(sentence2)
        print(res)

    finally:
        pass
