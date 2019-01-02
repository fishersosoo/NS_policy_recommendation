# 条件政策关系构建api说明

最后更新：2018年12月6日

具体调用可见 ns_ai_system/condition_identification/predicate_extraction/main.py


## 条件政策关系树生成接口

### 1：基于字符串构建

##### 参数：bytestr：字符串
##### 返回：关系树
##### 接口：tupletree_api.construct_tupletree_by_bytestr(bytestr)

### 2：基于文件路径构建

##### 参数：filename：文件路径
##### 返回：关系树
##### 接口：tupletree_api.construct_tupletree_by_file(filename)

## 关系树使用接口
### 1：遍历关系树
##### 返回：根据DFS遍历节点后的数组
##### 接口：get_all_nodes()
返回值示例：

```python
[{'TYPE': 'BONUS', 'CONTENT': '关于申报2017年度高新技术企业入统奖励'}, {'TYPE': 'LOGIC', 'CONTENT': 'AND'}, {'TYPE': 'CONDITION', 'CONTENT': three_tuple_entity(S={'tag': '税务征管关系及统计关系', 'field': '税务征管关系及统计关系'}, P={'tag': '在内'}, O={'tag': '广州市南沙区范围', 'location': '广州市南沙区'})}, {'TYPE': 'CONDITION', 'CONTENT': three_tuple_entity(S={'tag': ''}, P={'tag': '具有'}, O={'tag': '独立法人资格', 'qualification': '法人资格'})}, {'TYPE': 'CONDITION', 'CONTENT': three_tuple_entity(S={'tag': ''}, P={'tag': '实行'}, O={'tag': '独立核算', 'field': '核算'})}, {'TYPE': 'CONDITION', 'CONTENT': three_tuple_entity(S={'tag': '工商注册地址'}, P={'tag': '变更至'}, O={'tag': '南沙区', 'location': '南沙区'})}, {'TYPE': 'CONDITION', 'CONTENT': three_tuple_entity(S={'tag': ''}, P={'tag': '迁入', 'date-range': '2017年1月1日至2017年12月31日'}, O={'tag': '南沙区', 'location': '南沙区'})}, {'TYPE': 'CONDITION', 'CONTENT': three_tuple_entity(S={'tag': ''}, P={'tag': '具有'}, O={'tag': '高新技术企业资质', 'qualification': '高新技术企业资质'})}, {'TYPE': 'CONDITION', 'CONTENT': three_tuple_entity(S={'tag': '申报单位'}, P={'tag': '纳入', 'date-YEAR': '2017'}, O={'tag': '南沙区规模以上企业统计'})}]
```

#### 返回值说明：
返回的数组为节点数据字典的集合，在节点字典中有两个关键字：TYPE以及CONTENT

TYPE分为： BONUS、LOGIC、CONDITION 代表了事项名、逻辑关系、以及条件三元组 

其中LOGIC对应的值集为{AND,OR}，代表了与或关系。

CONDITION对应的值是元组类型three_tuple_entity(S,P,O),其中S、P、O对应的值都是字典，有以下关键字：

注：每个对应的字典值中都有tag关键字，其他不一定会有

对于S和O节点会有如下属性：

tag：在树上的节点显示内容，表示实体内容

type：实体类型（如果没识别出来实体就没有类型）

实体会分成以下类型：

- field，表示实体能和某个数据字段对应上
- location，表示地址值
- date，表示日期值
- literal，数值
- qualification，资质名称
- industry，行业
- scope，经营范围
- defined，在政策依据中自定义的实体（后续解析实现）
- event，事件，表示某个指标在发生改变（例如迁入南沙区）
- unknown，未知

对于S节点会有额外的for属性，表示这个三元组描述的对象是什么（如无此属性，则默认为company）

- person
- company
- project
- promise，描述承诺，例如spo节点对应的原文是“未来5年内不迁出南沙区”，时候描述的是承诺。