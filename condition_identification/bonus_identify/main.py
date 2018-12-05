# coding=UTF-8
from util import get_namecombine
from Tree import DocTree
import docx
from win32com import client as wc
import os
def doc2docx(doc_name,docx_name):
    # 首先将doc转换成docx
    word = client.Dispatch("Word.Application")
    doc = word.Documents.Open(doc_name)
    #使用参数16表示将doc转换成docx
    doc.SaveAs(docx_name,16)
    doc.Close()
    word.Quit()
def doc2txt(doc_name,txt_name):
    doc2docx(doc_name, 'tmp.docx')
    document = Document('tmp.docx')
    F=open(txt_name,'w')
    ps = document.paragraphs
    for x in ps:
        F.write(x.text)
        F.write('\n')
        print(x.text)
    F.close()
if __name__ == '__main__':
    files = os.listdir('doc')
    for f_name in files:
        print(f_name)
        tree = DocTree()
        tree.construct('doc/'+f_name)
        t=tree.get_bonus_tree()
        t.show()
    # tree = DocTree()
    # tree.construct('t.txt')
    # tree.get_tree().show()
    # b=tree.get_bonus_tree().show()












