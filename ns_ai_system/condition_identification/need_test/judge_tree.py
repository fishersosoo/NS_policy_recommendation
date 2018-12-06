import re
from pyhanlp import *
from treelib import Node,Tree

from collections import defaultdict
def get_namecombine(a, b, c):
    return a + b + str(c)
class DocTree:
    def __init__(self):
        self.d1 = {0: ['root']}
        self.d = {}
        self.tree = Tree()
    # 获取树
    def get_tree(self):
        return self.tree
    # 通过文档名字构建树
    def construct_from_bytes(self,bytes):
        text=bytes.decode("utf-8")
        html_list = []
        for line in text.split('\n'):
            # print(line)
            html_list.append(line.strip())
        self.parse_totree( html_list)

    def construct(self,filename):
        html_list=self.file_tolist(filename)
        self.parse_totree( html_list)
    # 读取文件成list
    def file_tolist(self,file):
        html_list = []
        with open(file, 'r', encoding='utf8') as f:
            for line in f.readlines():
                line=line.strip()
                if line:
                    html_list.append(line)
        return html_list
    # 解析html结构成树
    def parse_totree(self,html_list):
        level_words = [r'第.+章', r'第.+条', r'\d+\.', r'[一二三四五六七八九十]+、', r'\(\d+\)', r'\([一二三四五六七八九十]+\)',
                       r'（[一二三四五六七八九十]+）', 'r（\d+）',r'[①②③④⑤⑥⑦⑧⑨⑩]',r'第.+节']
        self.tree = Tree()
        tree = self.tree
        tree.create_node('root', 'root', data='partition')
        j = 0
        head=0

        h_level = 1
        id_key=None
        for i in range(0, len(html_list)):
            word = html_list[i]
            # 判断是否满足正则表达式，可否作为节点
            flag, key = self.is_node(level_words, word)
            if flag:
                # 根据j来构建独一无二的id
                id_key = key + str(j)
                # 确定属于第几层
                if key not in self.d:
                    self.d[key] = h_level
                    h_level += 1

                c_level = self.d[key]
                # 把第几层的id存起来
                if c_level not in self.d1:
                    self.d1[c_level] = [id_key]
                else:
                    self.d1[c_level].append(id_key)
                # 归属父节点即当前上一层最后一个id，即最近的上一层ID
                tree.create_node(word, id_key, self.d1[c_level - 1][-1], data=[word])
                j += 1
            else:
                # 如果当前不是一个节点，则把内容归属上一次最近的节点
                if id_key:
                    tree.get_node(id_key).data.append(word)
                else:
                    tree.create_node(word,key+str(head),'root', data=[word])
                    head+=1


    # 判断是否一个节点，即是否存在一些前缀词1.一.
    def is_node(self,level_words, word):
        word = word[0:10]
        Flag = False
        key = ''
        for level_word in level_words:
            re_result = re.search(level_word, word)
            if re_result:
                Flag = True
                key = level_word
                break
        return Flag, key

def show_tree(file_path):
    tree = DocTree()
    tree.construct(file_path)
    tree.get_tree().show()

