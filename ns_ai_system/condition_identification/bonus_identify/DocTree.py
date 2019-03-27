import queue
import re
import traceback

from treelib import Tree

from condition_identification.bonus_identify.util import *

"""
注意事项：
所有树的操作都是共享的，所以必须要使用copy函数new新的空间，哪怕是paste或者取子树，最后都是对同一个对象进行操作
"""


class DocTree:
    level_words = [r'第.+章', r'第.+条', r'\d+\.', r'[一二三四五六七八九十壱弐参四伍〇]+、', r'\(?\d+\)', r'\(?[一二三四五六七八九十]+\)',
                   r'（?[一二三四五六七八九十]+）', r'（?\d+）', r'[①②③④⑤⑥⑦⑧⑨⑩]', r'第.+节', '\d+、']

    def __init__(self):
        self.level_key = {0: ['root']}
        self.keys = ['root']
        self.idkeys = ['root']
        self.level_one = []
        self.tree = Tree()
        self.title = ''
        self.html_list = []

    def construct(self, input_str, from_file=False):
        """
        解析文档字符串，构建树结构

        :param input_str:
        :type from_file: bool
        :param from_file: 是否从文件中读取字符串
        :return:
        """
        self.__init__()
        try:
            if from_file:
                self.html_list = file_to_list(input_str)
            else:
                self.html_list = str_to_list(input_str)
            self.parse_to_tree(self.html_list)
        except Exception:
            self.tree = None
            traceback.print_exc()

    def parse_to_tree(self, html_list):
        """

        :param html_list:
        :return:
        """
        # 初始化
        title_flag = True
        j = 0
        head = 0
        id_key = None
        now_level = 0

        tree = self.tree
        tree.create_node('root', 'root', data=['partition'])
        for i in range(0, len(html_list)):
            word = html_list[i]
            if word == '':
                continue
            # 判断是否满足正则表达式，可否作为节点
            flag, key = self.get_candicate_node(self.level_words, word)
            # 处理申请条件后单独存在的一句话
            if i == 1 and flag == False:
                flag = True
                key = '：'
            # 这里说明一下：之前是认为层级是固定的，即如果一级是一。二级是1.那么二。3）这种就会报错，因为3）不会分为二级
            # 这里改过来了之后，前提条件是[一二三四五六七八九十]+、这个是每个文档都不会改变的，然后每一个层级都根据当前一级标题重新构造
            # if key==r'[一二三四五六七八九十壱弐参四伍〇]+、':
            #     h_level=1
            #     self.level_key = {0: ['root']}
            #     self.key_level = {}
            #     self.level_one.append(key + str(j))

            if flag:
                # 根据j来构建独一无二的id
                id_key = key + str(j)

                if key == '：':
                    now_level = 1
                    del self.keys[now_level + 1:]
                    del self.idkeys[now_level + 1:]
                if key != self.keys[now_level]:
                    if now_level - 1 > 0 and key == self.keys[now_level - 1] and self.keys[now_level] != '：':
                        now_level -= 1
                    else:
                        now_level += 1

                if now_level == len(self.keys):
                    self.keys.append(key)
                    self.idkeys.append(id_key)

                self.idkeys[now_level] = id_key

                tree.create_node(word, id_key, self.idkeys[now_level - 1], data=[word])
                j += 1

            else:
                # 如果当前不是一个节点，则把内容归属上一次最近的节点
                if id_key:
                    tree.get_node(id_key).data.append(word)
                    tree.get_node(id_key).tag += word
                else:
                    # 记录文章标题，即第一出现的不是节点
                    if title_flag:
                        self.title = word
                        title_flag = False
                    tree.create_node(word, key + str(head), 'root', data=[word])
                    head += 1

    def get_candicate_node(self, level_words, word):
        """
        判断是否一个节点，即是否存在一些前缀词1.一.
        :param level_words:
        :param word:
        :return:
        """
        Flag = False
        key = ''
        lword = word[0:5]
        for level_word in level_words:
            re_result = re.search(level_word, lword)
            if re_result:
                Flag = True
                key = level_word
                break

        if not Flag:
            if word[-1] == '：':
                Flag = True
                key = "："

        return Flag, key

    def get_tree(self):
        """
        获取树

        :return:
        """
        return self.tree

    def copy_tree(self, tree, new_id):
        """
        复制树

        :param tree: 原树
        :param new_id: 复制出来的树的id
        :return: 副本
        """
        new_tree = Tree()
        id_queue = queue.Queue()
        id_queue.put(tree.get_node(tree.root))
        while id_queue.qsize() > 0:
            node = id_queue.get()
            nid = node.identifier
            try:
                new_tree.create_node(identifier=new_id + '_' + nid, data=node.data, tag=node.tag,
                                     parent=new_id + '_' + tree.parent(nid).identifier)
            except:
                new_tree.create_node(identifier=new_id + '_' + nid, data=node.data, tag=node.tag)
            if tree.children(nid):
                for n in tree.children(nid):
                    id_queue.put(n)
        return new_tree


if __name__ == '__main__':
    # new_tree = Tree()
    # new_tree.create_node('a','a',data=[0,1])
    # for node in new_tree.expand_tree(nid='a', mode=Tree.DEPTH):
    #     print(new_tree[node].data)

    print(len('﻿'))
