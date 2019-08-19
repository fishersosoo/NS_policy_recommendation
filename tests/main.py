# coding=UTF-8
import sys
import re
sys.path.append("..")
from pyhanlp import *
from bonus_identify.Tree import DocTree
from treelib import Node,Tree
if __name__ == '__main__':
    tree=DocTree('../bonus_identify/广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')
    tree.construct()

    pytree = tree.get_tree()
    #print(pytree.all_nodes())
    bonuslist = tree.get_bonus_nodes()
    for bonus in bonuslist:
        subtree = Tree(pytree.subtree(bonus), deep=True)
        print(subtree.all_nodes())

        #print(pytree.get_node(bonus).data)
        #print(pytree.children(bonus))








