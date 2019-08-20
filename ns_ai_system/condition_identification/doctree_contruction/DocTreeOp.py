import datetime
import re
from condition_identification.doctree_contruction.util import file_to_list

def get_doctime(docTree):
    doc_tree = docTree.get_tree()
    c_nid = ''
    min_year = []
    if docTree.level_one:
        for nid in docTree.level_one:
            if '依据' in doc_tree.get_node(nid).data[0]:
                c_nid = nid
                break

        min_year = get_alltime(doc_tree, c_nid, min_year)
    else:
        print('请先构造篇章树')
        return None
    if min_year:
        return min(min_year)
    return datetime.datetime.utcnow().year


def get_alltime(doc_tree, c_nid, min_year):
    # 找自己
    p_data = doc_tree.get_node(c_nid).data
    del p_data[0]
    min_year.extend(judge_time(p_data))
    # 找儿子
    for children in doc_tree.children(c_nid):
        min_year.extend(judge_time(children.data))
    return min_year


def judge_time(data_list):
    result = []
    re_result = re.findall('2\d+', ','.join(data_list))
    for num_s in re_result:
        # 第一次过滤
        if len(num_s) == 4 and int(num_s) <= datetime.datetime.utcnow().year:
            result.append(int(num_s))
    if result:
        return [min(result)]
    return result


def get_handletime(DocTree):
    doc_tree = DocTree.get_tree()
    c_nid = ''
    time_word = "{0}年{1}月{2}日".format(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month,
                                      datetime.datetime.utcnow().day)
    if DocTree.level_one:
        for nid in DocTree.level_one:
            if '时间' in doc_tree.get_node(nid).data[0]:
                c_nid = nid
                break
        p_node = doc_tree.get_node(c_nid)
        if len(p_node.data) > 1:
            del p_node.data[0]
            time_word = ','.join(p_node.data)
        year = re.findall('\d+年', time_word)
        if year:
            year = max(year)
        else:
            year = str(datetime.datetime.utcnow().year)
        year_month_day = [year + i for i in re.findall('\d+月\d+日', time_word)]
        if year_month_day:
            min_time = min(year_month_day)
            max_time = max(year_month_day)
            return min_time, max_time
        else:
            raise Exception('找不到时间')
    else:
        raise Exception('请先构造DocTree')


def get_condition_content(DocTree):
    doc_tree = DocTree.get_tree()
    c_nid = ''
    content = ''
    if DocTree.level_one:
        for nid in DocTree.level_one:
            t = doc_tree.get_node(nid).data
            if '条件' in doc_tree.get_node(nid).data[0]:
                c_nid = nid
                break
        for children in doc_tree.children(c_nid):
            content += ','.join(children.data)
    else:
        print('请先构造篇章树')
        return None
    return content
def getTitle(ftext):
    result = ""
    ftexts = ftext.split('\n')
    for ft in ftexts:
        if len(ft.strip())>0:
            print(ft)
            result = ft
            break
    return result
