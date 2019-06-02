# coding=utf-8
"""
将数据列的过滤后的值进行储存
"""
from data_management.api.field_info import get_all_field_info
from data_management.api.field_info import get_field_values
from data_management.api.filtered_values import clean_up_filtered_values
from data_management.api.filtered_values import update_filtered_values
from condition_identification.util.specialcondition_identify import idf_address
from condition_identification.util.specialcondition_identify import idf_chinese_name
from condition_identification.util.specialcondition_identify import idf_contain_en
from condition_identification.util.specialcondition_identify import idf_contain_num
from condition_identification.database_process.database_parse import database_extract
from celery_task import log

def filtered_values_store():
    """
    1.清空field相关的filtered数据列
    2.获取所有field的数据列
    3.进行filter然后插入mongo数据库
    """
    all_field_info = get_all_field_info()
    clean_up_filtered_values()
    filtered_values(all_field_info)
    return True


def filtered_values(all_field_info):
    """
    不是所有的field都需要插入，满足特定条件的field才会被筛选插入

    Args:
        all_field_info : dict 每个field的相关描述信息

    """
    filtered_field_name = [] # 储存最后被filter的field名字
    baseinfo_filtered_field_name= [] # 储存企业基本信息的item_name
    for field_info in all_field_info:
        item_id = field_info['item_id']
        item_name = field_info['item_name']
        resource_name = field_info['resource_name']
        values = list(set(get_field_values(item_id)))[1:]
        if is_duplicate_baseinfo(item_name, baseinfo_filtered_field_name, filtered_field_name):
            continue
        if is_notqualified_values(values):
            continue
        update_values(item_name,values,filtered_field_name)
        # 保证重名情况下，取企业基本信息的值
        if resource_name == '企业基本信息':
            baseinfo_filtered_field_name.append(item_name)
    print(filtered_field_name)


def is_duplicate_baseinfo(item_name,baseinfo_filtered_field_name,filtered_field_name):
    """
    在item_name重名的情况下，保证企业基本信息的item_name优先级更高
    """
    if (item_name in filtered_field_name) and (item_name in baseinfo_filtered_field_name):
        return True
    else:
        return False


def is_notqualified_values(values_perfield):
    ## 过短筛选
    if len(values_perfield) < 5:
        return True
    is_notqualified = is_satisfied_conditions(values_perfield)
    return is_notqualified


def is_satisfied_conditions(values_perfield):
    # 数字，地名，英文，人名筛选
    for i in range(0, 5):
        sentence = values_perfield[i]
        if idf_contain_en(sentence) or idf_contain_num(sentence) or idf_address(sentence) or idf_chinese_name(sentence):
            return True
    return False


def update_values(item_name,values,filtered_field_name):
    filtered_values = database_extract(values)
    update_filtered_values(item_name, filtered_values)
    filtered_field_name.append(item_name)

if __name__=='__main__':
    a = ['经营状态', '经营业务范围', '行业领域', '行业名称', '专利名称', '软件分类', '股东类型', '出资币种', '职务', '变更事项', '出资币种', '企业经营状态', '认缴出资币种', '实缴币种', '许可文件名称', '职位名称', '学历', '资质名称', '具体情形', '公告分类']
    log.info(f"{a}")
    # filtered_values_store()
#     clean_up_filtered_values()
#     all_field_info = get_all_field_info()
#     filtered_field_name = []
#     filtered_id = []
#     baseinfo_filtered_field_name= []
#     for field_info in all_field_info:
#         item_id = field_info['item_id']
#         # item_id = 'OPSCOPE'
#         item_name = field_info['item_name']
#         resource_name = field_info['resource_name']
#
#         print(item_name)
#         if item_name in filtered_field_name and item_name in baseinfo_filtered_field_name:
#             continue
#
#
#         ## 过短筛选
#         values_perfield = list(set(get_field_values(item_id)))[1:]
#         if len(values_perfield) < 5:
#             continue
#         print(item_name)
#         # 数字，地名，英文，人名筛选
#         flag = False
#         num_pattern = re.compile('[0-9]+')
#         en_pattern = re.compile('[A-Za-z]+')
#         for i in range(0,5):
#             sentence = values_perfield[i]
#             num_match = num_pattern.findall(sentence)
#             en_match = en_pattern.findall(sentence)
#             if en_match or num_match or idf_address(sentence) or idf_chinese_name(sentence):
#                 flag = True
#                 break
#         if flag:
#             continue
#         print(item_name)
#
#
#         values_perfield = database_extract(values_perfield)
#         update_filtered_values(item_name, values_perfield)
#         filtered_field_name.append(item_name)
#         filtered_id.append(item_id)
#
#         # 保证重名情况下，取企业基本信息的值
#         if resource_name == '企业基本信息':
#             baseinfo_filtered_field_name.append(item_name)
#     #
#     # print(filtered_field_name)
#     # print(filtered_id)
#
#
#
#     # print(get_filtered_values('经营状态'))
#     # ['经营状态', '注册资本币种', '企业类型', '行业领域', '行业名称', '软件分类', '行业领域', '股东类型', '出资币种', '职务', '变更事项', '经营状态', '出资币种', '经营状态',
#     #  '企业经营状态', '认缴出资币种', '实缴币种', '许可文件名称', '学历', '具体情形', '公告分类']
#     # ['ENTSTATUS', 'REGCAPCUR', 'ENTTYPE', 'INDUSTRY', 'INDUSTRYCO', 'FRJ_RJFLH', 'FRJ_HYFLH', 'INVTYPE', 'CONCUR',
#     #  'POSITION', 'ALTITEM', 'ENTSTATUS', 'CONCUR', 'ENTSTATUS', 'ENTSTATUS', 'CONCUR', 'ACCCUR', 'XKNAME',
#     #  'FZPRH_EDUCATION', 'FSX_SXJTQX', 'FCT_CLASS']
# # ['经营状态', '企业类型', '经营业务范围', '行业领域', '行业名称', '软件分类', '行业领域', '股东类型', '出资币种', '职务', '变更事项', '经营状态', '出资币种', '经营状态', '
# # 企业经营状态', '认缴出资币种', '实缴币种', '许可文件名称', '职位名称', '学历', '资质名称', '具体情形', '公告分类']
#
# # 单个值要注意切割
#
# # 企业名称?
#
#
