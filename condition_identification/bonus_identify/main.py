# coding=UTF-8
import re
from Tree import DocTree
if __name__ == '__main__':
    tree=DocTree('广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')
    tree.construct()
    print(tree.get_bonus_nodes())








