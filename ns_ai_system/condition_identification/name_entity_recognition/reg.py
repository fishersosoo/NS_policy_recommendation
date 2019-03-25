import numpy as np
from name_entity_recognition.args import *
from pyhanlp import *
import numpy as np
from name_entity_recognition.Field import Field
from name_entity_recognition.Value import Value
from name_entity_recognition.extract import *
from bert_serving.client import BertClient
from name_entity_recognition.vectorize.extract_feature import BertVector
from name_entity_recognition.search import *


def getField_Value(word):
    if MODE == 'bert-util':
        bc = BertVector()
    else:
        bc = BertClient()
    keyword = extract_keyword(word, 2)
    field = Field(FILEPATH+'/field.txt')
    fielddict = field.constuct_fielddict(keyword, bc)
    value = Value(FILEPATH+'/evalue')
    valuedict = value.constuct_valuedict(keyword, bc)
    result = searchbyrelativepos(valuedict, fielddict, keyword)
    return result








if __name__=='__main__':
    # i=0
    # for  i in range(5,20):
    #     with open('data/'+str(i)+'.txt','r',encoding='utf8')as rf:
    #         for line in rf:
    #             word=line
    #             if MODE=='bert-util':
    #                 bc=BertVector()
    #             else:
    #                 bc = BertClient()
    #             keyword=extract_keyword(word, 2)
    #             print(keyword)
    #             field=Field('field.txt')
    #             fielddict=field.constuct_fielddict(keyword, bc)
    #             print(fielddict)
    #             value=Value('evalue')
    #             valuedict=value.constuct_valuedict(keyword,bc)
    #             print(valuedict)
    #             with open('data/'+str(i)+'_result.txt','a',encoding='utf8')as wf:
    #                 result=searchbyrelativepos(valuedict,fielddict,keyword)
    #                 for key in result:
    #                     wf.write(key)
    #                     wf.write(';')
    #                     wf.write(str(result[key]))
    #                     wf.write('\n')
    word='纳税大于5千万；'
    print(getField_Value(word))























