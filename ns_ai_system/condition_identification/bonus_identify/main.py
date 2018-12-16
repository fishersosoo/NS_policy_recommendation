# coding=UTF-8
from DocTreeOp import get_doctime
from DocTreeOp import get_handletime
from DocTreeOp import get_condition_content
from DocTree import DocTree
from treelib import Node,Tree
import os
# import docx
# from win32com import client as wc
#
# def doc2docx(doc_name,docx_name):
#     # 首先将doc转换成docx
#     word = client.Dispatch("Word.Application")
#     doc = word.Documents.Open(doc_name)
#     #使用参数16表示将doc转换成docx
#     doc.SaveAs(docx_name,16)
#     doc.Close()
#     word.Quit()
# def doc2txt(doc_name,txt_name):
#     doc2docx(doc_name, 'tmp.docx')
#     document = Document('tmp.docx')
#     F=open(txt_name,'w')
#     ps = document.paragraphs
#     for x in ps:
#         F.write(x.text)
#         F.write('\n')
#         print(x.text)
#     F.close()
if __name__ == '__main__':
    files = os.listdir('doc')
    for f_name in files:
        print(f_name)
        tree = DocTree()
        tree.construct('doc/'+f_name,1)
        t=tree.get_bonus_tree()
        t.show()
        print(get_condition_content(tree))


    # tree = DocTree()
    # tree.construct('2017年度专利质押融资贴息办事指南\n一、政策依据\n1.《广州南沙新区（自贸片区）促进科技创新产业发展扶持办法》（穗南开管办〔2017〕1号）第二十五条\n2.《广州南沙新区（自贸片区）促进科技创新产业发展扶持办法实施细则》（穗南开工科信〔2017〕13号）第三十九条\n二、申请条件',2)
    # tree.get_bonus_tree().show()













