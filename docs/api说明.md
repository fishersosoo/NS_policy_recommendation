# api接口说明
更新时间：2019/3/25
## 政策文本抽取（text_parsing.py）
###1. 文本解析构建条件树：

#### paragraph_extract()

参数：str：政策的文本内容

返回：tree：抽取后的条件树

#### triple_extract()
参数：tree:抽取后的条件树

返回：tree：抽取后的关系树

**关系树的结构如下：**

树中的每一个node有如下的三个属性：

- id:没有用

- data：叶子节点存储三元组，非叶子节点存储政策文本句子

- tag：str 非叶子节点存储and或or的字符串，叶子节点储存[]空数组

## 数据文本抽取(database_parse.py)
###1.数据库文本解析抽取
#### database_extract()
参数：
- list[str] 表示数据库该列的值
- outputname 表示数据库该列的列名。(到时候三元组的field就是这个名字)
- max_length 如果该列过长，耗时过长，debug的时候可以手动设置取多少行
