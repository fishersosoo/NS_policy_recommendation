# 结构树api说明

最后更新：2018年12月13日

具体调用可见 ns_ai_system\condition_identification\bonus_identify\main.py


## 条件政策关系树生成接口（DocTree.py）

###1：构建结构树

#####参数：str：字符串,int :1表示字符串为文件路径，2表示字符串为文本内容
#####返回：无
#####接口：DocTree.construct(str,int)

###2：获取优惠树

#####参数：无（需要先构建结构树才可调用）
#####返回：treeobject 优惠树
#####接口：DocTree.get_bonus_tree()

## 通用方法（util.py）
###1：获取文档时间
#####参数：object 传入的是Doc_Tree原始对象,不是任何通过get_tree返回的对象
#####返回：int 政策依据中对应的政策年份
#####接口：get_doctime()

