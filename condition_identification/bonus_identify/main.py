# coding=UTF-8
import re
def is_node(level_words,word):
    word=word[0:5]
    Flag=False
    key=''
    for level_word in level_words:
        re_result=re.search(level_word,word)
        if re_result:
            Flag=True
            key=level_word
            break
    return Flag,key

def list_tofile(file,begin,end,html_list):
    with open(file,'w',encoding='utf8') as f:
        for i in range(begin,end):
            word=html_list[i]
            f.write(word)
            f.write('\n')
def file_tolist(file):
    html_list=[]
    with open(file,'r',encoding='utf8') as f:
        for line in f.readlines():
            html_list.append(line.strip())
    return html_list


keywords=['奖','奖励','资助','补贴','补助','支持']
def patition_right_wrong(word,node_name,right_word,wrong_word):
    flag = 0
    for key in keywords:
        if key in word:
            right_word.append(node_name)
            flag = 1
            break
    if flag == 0:
        wrong_word.append(node_name)
    return  right_word,wrong_word






if __name__ == '__main__':
    html_list=file_tolist('广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')
    ###################################构树
    from treelib import Node,Tree

    level_words=[r'第.+章',r'第.+条',r'\d+\.',r'[一二三四五六七八九十]+、',r'\(\d+\)',r'\([一二三四五六七八九十]+\)',r'（[一二三四五六七八九十]+）','r（\d+）']

    level_title=['root']

    tree = Tree()
    tree.create_node('root','root',data='ds')
    j=0
    d={}
    d1={0:['root']}
    h_level=1
    for i in range(0,len(html_list)):
        word=html_list[i]
        # 判断是否满足正则表达式，可否作为节点
        flag,key =is_node(level_words,word)
        if flag:
            # 根据j来构建独一无二的id
            id_key=key+str(j)
            # 确定属于第几层
            if key not in d:
                d[key] = h_level
                h_level += 1

            c_level=d[key]
            # 把第几层的id存起来
            if c_level not in d1:
                d1[c_level]=[id_key]
            else:
                d1[c_level].append(id_key)
            # 归属父节点即当前上一层最后一个id，即最近的上一层ID
            tree.create_node(word,id_key,d1[c_level-1][-1],data=[word])
            j+=1
        else:
            # 如果当前不是一个节点，则把内容归属上一次最近的节点
            tree.get_node(id_key).data.append(word)

    tree.show()

#######################################优惠识别######################################



    right_word=[]
    wrong_word=[]
    if 1 not in d1:
        print('0')

    for node_name in d1[1]:
        word=''.join(tree.get_node(node_name).data)
        right_word, wrong_word=patition_right_wrong(word,node_name,right_word,wrong_word)



    while wrong_word:
        node_name=wrong_word.pop()
        for children_node in tree.children(node_name):
            word = ''.join(children_node.data)
            right_word, wrong_word = patition_right_wrong(word, children_node.identifier, right_word, wrong_word)
    print(right_word)








