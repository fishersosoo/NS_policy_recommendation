# 南沙政策推荐模块

python版本：3.6+

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