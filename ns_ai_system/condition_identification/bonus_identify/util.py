import re
import datetime
def get_doctime(DocTree):
    doc_tree=DocTree.get_tree()
    c_nid=''
    min_year=[]
    for nid in DocTree.level_key[1]:
        if '依据' in doc_tree.get_node(nid).data[0]:
            c_nid = nid
            break

    for children in doc_tree.children(c_nid):
        re_result = re.findall('2\d+',','.join(children.data))
        result=[]
        # 第一次过滤
        for num_s in re_result:
            if len(num_s)==4 and int(num_s)<=datetime.datetime.now().year:
                result.append(int(num_s))
            min_year.append(min(result))
    return min(min_year)