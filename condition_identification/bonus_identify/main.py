# coding=UTF-8
from util import get_namecombine
from Tree import DocTree
import os
if __name__ == '__main__':
    files = os.listdir('doc')
    for f_name in files:
        print(f_name)
        tree = DocTree()
        tree.construct('doc/'+f_name)
        t=tree.get_bonus_tree()









