from data_management.api import get_value_dic
from condition_identification.database_process.database_parse import data_filter

def data_store():
    value_dic = get_value_dic()
    for key in value_dic:
        values = data_filter(value_dic[key])
    # key :str列名
    # values:list 值
    raise NotImplementedError()






if __name__=='__main__':
    # print('完成')
    data_store()
    # print(redis_datafiltered.get('地址'))