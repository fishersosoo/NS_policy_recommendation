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

关系树的结构如下：

树中的每一个node有如下的三个属性：

- id:没有用

- data：[]list 其中每一个元素是Triple类，表示的是这一行含有的所有Triple集合

- tag：str 其中标识了and 和or以及其他(其他为文本的句子，因此只用判断and/or即可)。非叶子节点都会有and/or

## 数据文本抽取(database_parse.py)
###1.数据库文本解析抽取
#### database_extract()
参数：
- list[str] 表示数据库该列的值
- outputname 表示数据库该列的列名。(到时候三元组的field就是这个名字)
- max_length 如果该列过长，耗时过长，debug的时候可以手动设置取多少行
