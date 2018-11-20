import re
from treelib import Node,Tree
class DocTree:
    d1={0: ['root']}
    d={}
    tree=Tree()

    def __init__(self):
        pass
    # 获取树
    def get_tree(self):
        return self.tree
    # 通过文档名字构建树
    def construct(self,filename):
        html_list=self.file_tolist(filename)
        self.parse_totree( html_list)
    # 读取文件成list
    def file_tolist(self,file):
        html_list = []
        with open(file, 'r', encoding='utf8') as f:
            for line in f.readlines():
                html_list.append(line.strip())
        return html_list
    # 解析html结构成树
    def parse_totree(self,html_list):
        level_words = [r'第.+章', r'第.+条', r'\d+\.', r'[一二三四五六七八九十]+、', r'\(\d+\)', r'\([一二三四五六七八九十]+\)',
                       r'（[一二三四五六七八九十]+）', 'r（\d+）']
        self.tree = Tree()
        tree = self.tree
        tree.create_node('root', 'root', data='ds')
        j = 0
        d = self.d
        d1 = self.d1
        h_level = 1
        for i in range(0, len(html_list)):
            word = html_list[i]
            # 判断是否满足正则表达式，可否作为节点
            flag, key = self.is_node(level_words, word)
            if flag:
                # 根据j来构建独一无二的id
                id_key = key + str(j)
                # 确定属于第几层
                if key not in d:
                    d[key] = h_level
                    h_level += 1

                c_level = d[key]
                # 把第几层的id存起来
                if c_level not in d1:
                    d1[c_level] = [id_key]
                else:
                    d1[c_level].append(id_key)
                # 归属父节点即当前上一层最后一个id，即最近的上一层ID
                tree.create_node(word, id_key, d1[c_level - 1][-1], data=[word])
                j += 1
            else:
                # 如果当前不是一个节点，则把内容归属上一次最近的节点
                tree.get_node(id_key).data.append(word)
        tree.show()

    # 判断是否一个节点，即是否存在一些前缀词1.一.
    def is_node(self,level_words, word):
        word = word[0:5]
        Flag = False
        key = ''
        for level_word in level_words:
            re_result = re.search(level_word, word)
            if re_result:
                Flag = True
                key = level_word
                break
        return Flag, key


    ########################### 识别奖励
    keywords = ['奖', '奖励', '资助', '补贴', '补助', '支持']
    # 划分正误，正确的就不需要再往下搜索，错误的就需要往下一层继续搜索
    def patition_right_wrong(self,word, node_name, right_word, wrong_word):
        flag = 0
        for key in self.keywords:
            if key in word:
                right_word.append(node_name)
                flag = 1
                break
        if flag == 0:
            wrong_word.append(node_name)
        return right_word, wrong_word



    def get_bonus_nodes(self):
        right_word=[]
        wrong_word=[]
        if 1 not in self.d1:
            return None
        # 搜索的过程
        for node_name in self.d1[1]:
            word=''.join(self.tree.get_node(node_name).data)
            right_word, wrong_word=self.patition_right_wrong(word,node_name,right_word,wrong_word)
        while wrong_word:
            node_name=wrong_word.pop()
            for children_node in self.tree.children(node_name):
                word = ''.join(children_node.data)
                right_word, wrong_word = self.patition_right_wrong(word, children_node.identifier, right_word, wrong_word)
        return right_word