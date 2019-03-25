import re

from bonus_identify.util import *
from treelib import Node,Tree
import queue
from collections import defaultdict
# 注意事项：
# 所有树的操作都是共享的，所以必须要使用copy函数new新的空间，哪怕是paste或者取子树，最后都是对同一个对象进行操作


class DocTree:

        def __init__(self):
            self.clean()
        def clean(self):
            self.level_key = {0: ['root']}
            self.keys = ['root']
            self.idkeys = ['root']
            self.level_one=[]
            self.tree = Tree()
            self.title=''
            self.html_list=[]
# 构造结构树

        # 通过文档名字构建树
        def construct(self,str,type):
            self.clean()
            try:
                if type == 1:
                    self.html_list = file_tolist(str)
                if type == 2:
                    self.html_list = str_tolist(str)
                self.parse_totree(self.html_list)
            except Exception as  e:
                self.tree=None
                print('error')




        # 解析html结构成树
        level_words = [r'第.+章', r'第.+条', r'\d+\.', r'[一二三四五六七八九十壱弐参四伍〇]+、', r'\(?\d+\)', r'\(?[一二三四五六七八九十]+\)',
                       r'（?[一二三四五六七八九十]+）', r'（?\d+）', r'[①②③④⑤⑥⑦⑧⑨⑩]', r'第.+节', '\d+、']
        def parse_totree(self,html_list):
            # 初始化
            title_flag=True
            j = 0
            head = 0
            id_key = None
            now_level=0

            tree=self.tree
            tree.create_node('root', 'root', data=['partition'])
            for i in range(0, len(html_list)):
                word = html_list[i]
                if word=='':
                    continue
                # 判断是否满足正则表达式，可否作为节点
                flag, key = self.get_candicate_node(self.level_words, word)
                # 处理申请条件后单独存在的一句话
                if i==1 and flag==False:
                    flag=True
                    key='：'
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

                    if key =='：':
                        now_level=1
                        del self.keys[now_level+1:]
                        del self.idkeys[now_level+1:]
                    if key !=self.keys[now_level] :
                        if now_level-1>0 and  key ==self.keys[now_level-1] and self.keys[now_level]!='：':
                            now_level-=1
                        else:
                            now_level+=1

                    if now_level==len(self.keys):
                        self.keys.append(key)
                        self.idkeys.append(id_key)

                    self.idkeys[now_level]=id_key


                    tree.create_node(word, id_key, self.idkeys[now_level-1], data=[word])
                    j += 1


                    # # 确定属于第几层
                    # if key not in self.key_level:
                    #     self.key_level[key] = h_level
                    #     h_level += 1
                    # c_level = self.key_level[key]
                    # # 把第几层的id存起来
                    # if c_level not in self.level_key:
                    #     self.level_key[c_level] = [id_key]
                    # else:
                    #     self.level_key[c_level].append(id_key)
                    # # 归属父节点即当前上一层最后一个id，即最近的上一层ID
                    # tree.create_node(word, id_key, self.level_key[c_level - 1][-1], data=[word])
                    # j += 1
                else:
                    # 如果当前不是一个节点，则把内容归属上一次最近的节点
                    if id_key:
                        tree.get_node(id_key).data.append(word)
                        tree.get_node(id_key).tag+=word
                    else:
                        # 记录文章标题，即第一出现的不是节点
                        if title_flag:
                            self.title=word
                            title_flag=False
                        tree.create_node(word,key+str(head),'root', data=[word])
                        head+=1


        # 判断是否一个节点，即是否存在一些前缀词1.一.
        def get_candicate_node(self,level_words, word):
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








# 通用方法
        # 获取树
        def get_tree(self):
            return self.tree
        def copy_tree(self,tree,diff):
            '''
            :param tree: 原树
            :param diff: 需要修改的id的后缀
            :return: 树的复制
            '''
            new_tree=Tree()
            id_queue=queue.Queue()
            id_queue.put(tree.get_node(tree.root))
            while id_queue.qsize()>0:
                node=id_queue.get()
                nid=node.identifier
                try:
                    new_tree.create_node(identifier=diff+'_'+nid,data=node.data,tag=node.tag,parent=diff+'_'+tree.parent(nid).identifier)
                except:
                    new_tree.create_node(identifier=diff + '_' + nid, data=node.data, tag=node.tag)
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




































        ########################### 识别奖励(带数词量词和句法分析)

        # keywords = ['奖', '奖励', '资助', '补贴', '补助', '支持','资金']
        #
        # # 识别量词和数词 q和m必须两个同时都有
        # def identify_quantifier(self,parse_words,i,interval):
        #     flag=False
        #     m_flag=False
        #     q_flag=False
        #     if i<0:
        #         i = 0
        #
        #     while i<len(parse_words) and i <=i+interval:
        #         term = parse_words[i]
        #         if str(term.nature)=='m' or str(term.nature)=='mq':
        #             m_flag=True
        #         if str(term.nature)=='q':
        #             q_flag=True
        #         if m_flag and q_flag:
        #             flag=True
        #             break
        #         i+=1
        #     return flag
        #
        #
        # # 句法依存识别
        # def identify_dependency(self,sentence,key):
        #     word_array = HanLP.parseDependency(sentence).getWordArray()
        #     parse_dict=defaultdict(list)
        #     flag=False
        #     # 构造字典
        #     for word in word_array:
        #         if word.LEMMA in parse_dict:
        #             parse_dict[word.LEMMA].extend([word.DEPREL, word.HEAD.LEMMA])
        #         else:
        #             parse_dict[word.LEMMA] = [word.DEPREL, word.HEAD.LEMMA]
        #     # 构造动宾结构
        #     for i in range(0,len(parse_dict[key]),2):
        #         if parse_dict[key][i]=='动宾关系':
        #             flag=True
        #             break
        #
        #
        #     # 如果并列就往上找动宾
        #     if not flag:
        #         while '并列关系' in parse_dict[key]:
        #             for i in range(0,len(parse_dict[key]),2):
        #                 if parse_dict[key][i]=='并列关系':
        #                     parse_dict[key].pop(i)
        #                     # 因为pop下标就改变了出来两次
        #                     key=parse_dict[key].pop(i)
        #                     break
        #     return flag
        #
        #
        #
        # # 识别优惠
        # def identify_bonus(self,word):
        #     flag=False
        #     parse_words=HanLP.segment(word)
        #     for i in range(len(parse_words)):
        #         term=parse_words[i]
        #         for key in self.keywords:
        #             if key in term.word:
        #                 # 加入量词的查找，取关键词所在的前后几个词之内看是否存在量词
        #                 if self.identify_quantifier(parse_words,i-10,10)==False:
        #                     flag=self.identify_quantifier(parse_words,i,10)
        #                 else:
        #                     flag=True
        #                 # 再量词识别的基础上识别依赖关系
        #                 if flag:
        #                     flag=self.identify_dependency(word,term.word)
        #     return flag
        #
        #
        # def get_bonus_nodes(self):
        #     right_word=[]
        #     return self.dfs('root',right_word)
        # def dfs(self,node_name,right_word):
        #     node=self.tree.get_node(node_name)
        #     word = ''.join(node.data)
        #     if self.identify_bonus(word):
        #         right_word.append(node_name)
        #     if node.is_leaf():
        #         return right_word
        #     else:
        #         for children_node in self.tree.children(node_name):
        #             right_word=self.dfs(children_node.identifier,right_word)
        #     return right_word
        #
        # def get_bonus_tree(self):
        #     bonus_tree=Tree()
        #     doc_tree=self.get_tree()
        #     bonus_tree.create_node('root','root')
        #     bonus_node_names=self.get_bonus_nodes()
        #     for bonus_node_name in bonus_node_names:
        #         bonus_node=self.tree.get_node(bonus_node_name)
        #         if bonus_node.is_leaf():
        #             b_name=get_namecombine('b',bonus_node.identifier,0)
        #             c_name=get_namecombine('c',bonus_node.identifier,0)
        #             bonus_tree.create_node(bonus_node.data,b_name,parent='root')
        #             bonus_tree.create_node(bonus_node.data,c_name, parent=b_name)
        #             bonus_tree=self.findparent(b_name,bonus_node_name,c_name,bonus_node_names,bonus_tree,doc_tree)
        #     bonus_tree.show()
        #     return bonus_tree
        #
        #
        #
        #
        # def findparent(self,b_name,n_name,c_name,bonus_node_names,bonus_tree,tree):
        #     # 记录叶子结点-固定
        #     leave_name=b_name
        #     # 记录初始位置-会一直变化
        #     node_name=n_name
        #     diff=0
        #     while node_name!='root':
        #         parent=tree.parent(node_name)
        #         parent_name=parent.identifier
        #
        #
        #         if parent_name in bonus_node_names:
        #             p_name=get_namecombine('b',parent_name,0)
        #             # 为了避免id重复定义的一个区别符
        #             while bonus_tree.get_node(p_name):
        #                 diff+=1
        #                 p_name = get_namecombine('b', parent_name, diff)
        #             bonus_tree.create_node(parent.data,p_name,parent='root')
        #             # 都是从子移动到父亲下面
        #             bonus_tree.move_node(b_name,p_name)
        #
        #             b_name=p_name
        #             diff=0
        #
        #
        #         cp_name=get_namecombine('c',parent_name,0)
        #         while bonus_tree.get_node(cp_name):
        #             diff+=1
        #             cp_name = get_namecombine('c', parent_name, diff)
        #         bonus_tree.create_node(parent.data, cp_name, parent=leave_name)
        #         # 都是从子移动到父亲下面
        #         bonus_tree.move_node(c_name, cp_name)
        #         diff = 0
        #         c_name=cp_name
        #         node_name = parent_name
        #     return bonus_tree

# # 识别优惠树
#         keywords = ['奖', '奖励', '资助', '补贴', '补助', '支持', '资金'] # 奖励识别的关键字
#         # 只识别条件了
#         def get_bonus_tree(self):
#             bonus_tree=Tree()
#             doc_tree=self.get_tree()
#             c_nid=''
#             b_nid=''
#             b_data=''
#             # 寻找条件
#             for nid in self.level_one:
#                 if '条件'in doc_tree.get_node(nid).data[0]:
#                     c_nid=nid
#                     break
#             # 寻找优惠
#             for nid in self.level_one:
#                 for key in self.keywords:
#                     if key in doc_tree.get_node(nid).data[0]:
#                         b_nid=nid
#                         break
#             if b_nid!='' and c_nid!='':
#                 for node in doc_tree.expand_tree(nid=b_nid, mode=Tree.DEPTH):
#                     if node==b_nid:
#                         p_nodedata=doc_tree[node].data.copy()
#                         del p_nodedata[0]
#                         # 把‘四.奖励标准’过滤掉
#                         b_data += ','.join(p_nodedata)
#                         continue
#                     b_data+=','.join(doc_tree[node].data)
#             #  创建优惠树
#                 bonus_tree.create_node(identifier='root',tag=b_data,data=b_data)
#                 bonus_tree.create_node('partition', 'partition', parent='root')
#
#
#                 # 父节点可能会有信息，因为有可能他没有序号就是一段话
#                 p_data=doc_tree.get_node(c_nid).data.copy()
#
#                     # 把‘二.申请条件’和‘满足以下条件’删除
#                 if len(p_data)>=2:
#                     if len(p_data[0])<8 :
#                         del p_data[0]
#                     if '：' in p_data[0]:
#                         del p_data[0]
#                     p_data=','.join(p_data)
#                     if p_data:
#                         bonus_tree.create_node(identifier=c_nid, tag=p_data, data=p_data,parent='partition')
#                 # 可以继续改进，这里用树的复制其实是浪费了资源
#                 new_tree=self.copy_tree(doc_tree.subtree(c_nid),'')
#                 for children in new_tree.children(''+'_'+c_nid):
#                     bonus_tree.paste('partition', new_tree.subtree(children.identifier))
#             return bonus_tree

