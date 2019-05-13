# api接口说明
更新时间：2019/3/25
## 政策文本抽取（text_parsing.py）
###1. 文本解析构建条件树：

#### paragraph_extract()

参数：str：政策的文本内容

返回：tree：抽取后的条件树

#### triple_extract()
参数：tree:抽取后的条件树

**关系树的结构如下：**

树中的每一个node有如下的三个属性：

- id:没有用

- data：叶子节点存储三元组，非叶子节点存储政策文本句子

- tag：str 非叶子节点存储and或or的字符串，叶子节点储存[]空数组

返回：triples:triple的数组，有可能多个tirple的sentence_id相同，因为都是同一个句子出来

triple结构：

- field:数据库列字段

- relation:关系

- value：值
 
- sentence：所在句子

- sentence_id:所在句子的id

all_sentence： 字典{id:sentence}
- id：与triple中的sentence_id对应
- sentence：政策条件句子

对接：一个句子只要有一个三元组满足就算满足，然后遍历




