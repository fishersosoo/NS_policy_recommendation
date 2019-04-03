# coding=utf-8

import queue
import re
import traceback
from treelib import Tree
from condition_identification.bonus_identify.util import str_to_list
from condition_identification.bonus_identify.util import file_to_list

"""
注意事项：
所有树的操作都是共享的，所以必须要使用copy函数new新的空间，哪怕是paste或者取子树，最后都是对同一个对象进行操作
"""
level_words = [r'第.+章', r'第.+条', r'\d+\.', r'[一二三四五六七八九十壱弐参四伍〇]+、', r'\(?\d+\)', r'\(?[一二三四五六七八九十]+\)',
               r'（?[一二三四五六七八九十]+）', r'（?\d+）', r'[①②③④⑤⑥⑦⑧⑨⑩]', r'第.+节', '\d+、']


class DocTree(object):
    """政策条件树

    从政策文本中抽取信息，每一行作为一个节点
    主要在于只保留了政策条件的内容以及政策各条的层次关系

    Attributes:
        keys: list 元素可以重复；存储的是满足的正则表达式，以此来区分不同的层次
        id_keys: list 每一个元素独一无二；存储的是树的每个节点的id，因为要求每个节点的id都不能重复，所以以此为索引找到其对应的父节点和子节点。
        tree: Tree 用来存储每个节点的树结构
        html_list: list 每一个元素即政策文本的一行，是读取政策文本后的结果
    """

    def __init__(self):
        """初始化"""
        self.keys = ['root']
        self.id_keys = ['root']
        self.tree = Tree()
        self.html_list = []

    def construct(self, input_str, from_file=False):
        """解析文档字符串，构建树结构

        Args:
            input_str: str 文本字符串，或文档所在的路径字符串
            from_file: bool 是否从文件中读取字符串

        Raises:
            解析的过程中可能会出现各种错误

        """
        if from_file:
            self.html_list = file_to_list(input_str)
        else:
            self.html_list = str_to_list(input_str)
        try:
            self.tree = self.__parse_to_tree(self.html_list)
        except Exception:
            self.tree = None
            traceback.print_exc()

    def get_tree(self):
        """
        获取树
        :return:
        """
        return self.tree

    @staticmethod
    def copy_tree(tree, new_id):
        """
        复制树
        :param tree: 原树
        :param new_id: 复制出来的树的id=new_id+_+旧id
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

    def __parse_to_tree(self, html_list):
        """政策文本结构的构建

        Args:
            html_list: str 政策文本字符串

        Returns:
            构造的政策结构树
            Tree: Node
            Node: data/tag
            data: list 元素为每一行文本，有可能政策文本中多行表示一点
            tag: str data的文本表示
        """
        unique_name_tag = 0  # 用计数来构造唯一的id
        id_key = None
        now_level = 0  # 记录当前所在的层级
        tree = Tree()
        tree.create_node('root', 'root', data=['partition'])
        for i in range(0, len(html_list)):
            word = html_list[i]
            if word == '':
                continue
            is_node, key = self.__get_candicate_node(word)  # 判断可否作为节点,返回判断结果和判断依据

            lword=word[0:5]
            for level_word in level_words:
                lword = re.sub(level_word, '',lword)
            word=lword+word[5:]

            # 处理申请条件后单独存在的一句话
            # Example:二、申请条件  位于南沙区内
            if i == 1 and not is_node:
                is_node = True
                key = '：'
            if is_node:
                id_key = key + str(unique_name_tag)
                # 层级结构的构建逻辑：
                # 如果有冒号，即满足以下条件：   这时候层级重新定义为1，它为最初层
                # 如果非冒号，即满足了正则表达，具有标题性质，如果它与当前层的key一致，则为同级，如果与上层key一致，则为上一级，否则则为下一级
                if key == '：':
                    now_level = 1
                    del self.keys[now_level + 1:]
                    del self.id_keys[now_level + 1:]
                if key != self.keys[now_level]:
                    if now_level - 1 > 0 and key == self.keys[now_level - 1] and self.keys[now_level] != '：':
                        now_level -= 1
                    else:
                        now_level += 1
                # 新创建一级
                if now_level == len(self.keys):
                    self.keys.append(key)
                    self.id_keys.append(id_key)
                self.id_keys[now_level] = id_key
                tree.create_node(word, id_key, self.id_keys[now_level - 1], data=[word])
                unique_name_tag += 1
            else:
                # 如果当前不是一个节点，则把内容归属上一次最近的节点
                if id_key:
                    tree.get_node(id_key).data.append(word)
                    tree.get_node(id_key).tag += word
        return tree

    def __get_candicate_node(self, word):
        """正则表达式判断节点

        Args:
            word: str 需要判断的文本

        return:
            is_bode: boolean True表示该行文本为节点,False表示改行文本不为节点
            key: str 满足的正则表达式，把它作为每一层的id记录下来
        """
        is_node = False
        key = ''
        lword = word[0:5]  # 只取句子的前五个字，为了避免在句子其他地方会不小心匹配上了正则表达式
        for level_word in level_words:
            re_result = re.search(level_word, lword)
            if re_result:
                is_node = True
                key = level_word
                break

        # 政策文本中有这样的情况：满足以下所有条件：
        # 此时句子开头没有标号，所以用句末的：来判断
        if not is_node:
            if word[-1] == '：':
                is_node = True
                key = "："

        return is_node, key

if __name__ == '__main__':
    # new_tree = Tree()
    # new_tree.create_node('a','a',data=[0,1])
    # for node in new_tree.expand_tree(nid='a', mode=Tree.DEPTH):
    #     print(new_tree[node].data)

    t = DocTree()
    t.construct('F:\\txt\\txt\\0.txt')
    t.get_tree().show()
