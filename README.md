# 南沙政策推荐模块

python版本：3.6+
java版本: 9.0.1 (pyhanlp库需要依赖java环境）

如仍然出现下列错误：

jpype._jvmfinder.JVMNotFoundException: No JVM shared library file (jvm.dll) found. Try setting up the JAVA_HOME environment variable properly.

则需要添加一个JAVA_HOME变量，变量值为java的bin目录的绝对路径

请勿将python虚拟环境上传。

每次在虚拟环境安装新的包后，记得更新requirements.txt。

```
pip freeze > requirements.txt
```

## 项目结构

项目资源例如政策文件、字典文件放在res目录下。可运行的二进制文件放在bin目录下。condition_identification目录下为从政策文件中识别条件的python包。

文档放在docs目录下，目前还没将之前的文档上传。

## 数据库配置

neo4j数据库

http地址：http://cn.fishersosoo.xyz:7474

bolt地址：bolt://cn.fishersosoo.xyz:7687

用户名：neo4j

密码：1995

## hanlp库配置
首次部署环境/依赖词典或数据库有更新时，调用HanlpSynataxAnalysis.reloadHanlpCustomDictionary函数：
      
      def reloadHanlpCustomDictionary(self,dict_path)
      
参数传入dict_path的路径

## 优惠&&条件智能理解相关注意事项
运行 demo代码如下:

      from bonus_identify.Tree import DocTree
      from predicate_extraction.tuple_bonus_recognize import TupleBonus

      def test_subtree():
          tree=DocTree()
          tree.construct('../bonus_identify/广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt')
          dict_dir=r"Y:\Nansha AI Services\condition_identification\res\word_segmentation"
          tuplebonus = TupleBonus(dict_dir)
          tuplebonus.bonus_tuple_analysis(tree)
          bonus_tree = tuplebonus.get_bonus_tree()
    
      if __name__ == "__main__":
          test_subtree()

打印结果为优惠与条件的关系，以多叉树结构展示
通过函数 get_bonus_tree（）获得条件优惠树

## 条件优惠树相关函数
      def get_all_bonus(self):
      
获取该树的所有优惠内容
      
      
      def get_node_data(self,node):
     
函数参数为节点，返回节点的data。data为字典形式，包括 TYPE 以及 CONTENT 两个关键词，指种类和内容

TYPE：
[POLICY,BONUS,LOGIC,CONDITION]

CONTENT:
[POLICY对应的CONTENT为空;

BONUS对应的CONTENT为优惠内容;

LOGIC对应的CONTENT为 “AND”/“OR”;

CONDITION对应的CONTENT为SPO三元组,定义如下：('three_tuple_entity', ['S','P','O'])]
 
该多叉树的其他函数调用可参考https://blog.csdn.net/kalbertlee/article/details/70158015 或者 https://treelib.readthedocs.io/en/latest/
            
