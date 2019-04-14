# coding=utf-8
import os
from data_management.api import get_num_fields
from data_management.api import get_address_fields

# 数据库所有列值数字的field值
NUMS = get_num_fields()

# 数据库列值为地址的field值
ADDRESS = get_address_fields()

# 相似度值 field 和 value值里面相似度比较的值
similarity_value = 0.945

# 数据库列值数据聚类的最小长度，数据太少没有聚类的必要
database_cluster_min_length = 300

# 数据库值过多只取前max_length条
database_cluster_max_length = 2000

# 对数据库数据聚类的相似度要求
database_cluster_similarity = 0.9

# 聚类后去相似度最高的分位数值
database_cluster_quantile = 0.4

# 关键词抽取阙值设置
keyword_len_threshold = 2

# 关系抽取的关键字
dayu = ['大于', '以上', '超过', '多于', '高于', '至多', '以后']
budayu = ['不' + x for x in dayu]
xiaoyu = ['小于', '以下', '少于', '低于', '至少', '未满', '以前']
buxiaoyu = ['不' + x for x in xiaoyu]
weiyu = ['位于', '区内', '范围内', '在']
fou = ['无', '不']
# 计算余弦相似度的bias 和系数
cos_similarity_bias = 0.5
cos_similarity_multiplier = 0.5

# 对有多个field值的进一步抽取，相同的字数限制
field_has_word_count = 2
