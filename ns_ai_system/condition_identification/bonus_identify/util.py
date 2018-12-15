import re
import datetime
def get_doctime(DocTree):
    doc_tree=DocTree.get_tree()
    c_nid=''
    min_year=[]
    if DocTree.level_key:
        for nid in DocTree.level_key[1]:
            if '依据' in doc_tree.get_node(nid).data[0]:
                c_nid = nid
                break

        min_year=get_alltime(doc_tree,c_nid,min_year)
    else:
        print('请先构造篇章树')
        return None
    if min_year:
        return min(min_year)
    return datetime.datetime.now().year

def get_alltime(doc_tree,c_nid,min_year):
    # 找自己
    p_data=doc_tree.get_node(c_nid).data
    del p_data[0]
    min_year.extend(judge_time(p_data))
    # 找儿子
    for children in doc_tree.children(c_nid):
            min_year.extend(judge_time(children.data))
    return min_year

def judge_time(data_list):
    result=[]
    re_result = re.findall('2\d+', ','.join(data_list))
    for num_s in re_result:
        # 第一次过滤
        if len(num_s) == 4 and int(num_s) <= datetime.datetime.now().year:
            result.append(int(num_s))
    if result:
        return [min(result)]
    return result


def get_handletime(DocTree):
    doc_tree=DocTree.get_tree()
    c_nid=''
    time_word="{0}年{1}月{2}日".format(datetime.datetime.now().year,datetime.datetime.now().month,datetime.datetime.now().day)
    if DocTree.level_key:
        for nid in DocTree.level_key[1]:
            if '时间' in doc_tree.get_node(nid).data[0]:
                c_nid = nid
                break

        p_node=doc_tree.get_node(c_nid)
        if len(p_node.data)>1:
            del p_node.data[0]
            time_word=','.join(p_node.data)
        year = re.findall('\d+年', time_word)
        year=max(year)
        year_month_day=[year+i for i in re.findall('\d+月\d+日', time_word)]
        min_time=min(year_month_day)
        max_time=max(year_month_day)
        return min_time,max_time
    else:
        print('请先构造篇章树')
        return None


