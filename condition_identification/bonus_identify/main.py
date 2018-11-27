# coding=UTF-8
from util import get_namecombine
from Tree import DocTree
if __name__ == '__main__':
    tree=DocTree()
    tree.construct('广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')
    t=tree.get_bonus_tree()

    count=0
    while t.get_node(get_namecombine('c','root',count)):
        print(t.get_node(get_namecombine('c','root',count)))
        count+=1










