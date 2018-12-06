# 条件政策关系构建api说明

最后更新：2018年12月6日

具体调用可见 ns_ai_system/condition_identification/predicate_extraction/main.py


## 条件政策关系树生成接口

###1：基于字符串构建

#####参数：bytestr：字符串
#####返回：关系树
#####接口：tupletree_api.construct_tupletree_by_bytestr(bytestr)

###2：基于文件路径构建

#####参数：filename：文件路径
#####返回：关系树
#####接口：tupletree_api.construct_tupletree_by_file(filename)

## 关系树使用接口
###1：遍历关系树
#####返回：根据DFS遍历节点后的数组
#####接口：get_all_nodes()
返回值示例：[{'TYPE': 'BONUS', 'CONTENT': '关于申报2017年度高新技术企业入统奖励'}, {'TYPE': 'LOGIC', 'CONTENT': 'AND'}, {'TYPE': 'CONDITION', 'CONTENT': '税务关系, 在, 广州市南沙区范围内'}, {'TYPE': 'CONDITION', 'CONTENT': ', 具有, 独立法人资格'}, {'TYPE': 'CONDITION', 'CONTENT': ', 有, 健全财务制度'}, {'TYPE': 'CONDITION', 'CONTENT': ', 实行, 独立核算'}, {'TYPE': 'CONDITION', 'CONTENT': '申报单位地址, 变更, '}, {'TYPE': 'CONDITION', 'CONTENT': ', 迁入, 南沙区时间'}, {'TYPE': 'CONDITION', 'CONTENT': ', 具有, 高新技术企业资质'}, {'TYPE': 'CONDITION', 'CONTENT': '申报单位, 纳入, 统计'}]
####返回值说明：
返回的数组为节点数据字典的集合，在节点字典中有两个关键字：TYPE以及CONTENT

TYPE分为： BONUS、LOGIC、CONDITION 代表了事项名、逻辑关系、以及条件三元组 

其中LOGIC对应的值集为{AND,OR}，代表了与或关系。

CONDITION对应的值是以逗号','分割的三元组字符串，通过逗号分割可获得S、P、O三个值