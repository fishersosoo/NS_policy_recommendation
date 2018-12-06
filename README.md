# 南沙政策智能平台

## 项目结构与规范

| 目录                                    | 作用                      | 注意事项                                                     |
| --------------------------------------- | ------------------------- | ------------------------------------------------------------ |
| ./bin                                   | 存放脚本及可执行文件      | 应在发布可部署版本时候将系统环境配置、服务启动、测试脚本都放在这里 |
| ./bin/linux                             | linux系统执行文件         |                                                              |
| ./bin/windows                           | windows系统执行文件       |                                                              |
| ./docs                                  | 存放文档                  | 根目录下存放markdown文件便于进行文档的版本控制               |
| ./docs/pdf                              | 存放文档对应的pdf格式文件 | 更新md文档之后需要导出pdf到这里                              |
| ./ns_ai_system                          | 存放源代码及相关资源      |                                                              |
| ./ns_ai_system/res                      | 存放资源                  | 请将所有非代码内容放在这里，包括政策文件、词典               |
| ./ns_ai_system/condition_identification | 政策理解核心源代码        |                                                              |
| ./ns_ai_system/data_management          | 数据库相关代码            |                                                              |
| ./ns_ai_system/restful_server           | restful服务相关代码       |                                                              |
| ./tests                                 | 测试代码                  | 在测试脚本中需要导入包通过`sys.path.insert`来导入。测试文档要放在`./docs` |
|                                         |                           |                                                              |

不同模块的函数调用和代码说明放在`./docs`下，不要放在这里了。

请勿将python虚拟环境上传。

每次在虚拟环境安装新的包后，记得更新requirements.txt。

`pip freeze > requirements.txt`

## 配置需求概述

python版本： 3.6.7

java版本: 9.0.1 (pyhanlp库需要依赖java环境）

如仍然出现下列错误：

jpype._jvmfinder.JVMNotFoundException: No JVM shared library file (jvm.dll) found. Try setting up the JAVA_HOME environment variable properly.

则需要添加一个JAVA_HOME变量，变量值为java的bin目录的绝对路径

## 数据库配置

neo4j数据库

http地址：http://ns.fishersosoo.xyz:7474

bolt地址：bolt://ns.fishersosoo.xyz:7687

用户名：neo4j

密码：1995
