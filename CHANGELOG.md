# 更新日志

此项目的所有显着更改都应记录在此文件中。

文件格式参照[如何维护更新日志](https://keepachangelog.com/zh-CN/1.0.0/)，本项目的版本号必须符合[语义化版本](https://semver.org/lang/zh-CN/)规范。

## [Unreleased]

### Added

- 添加restful接口，/policy/check_recommend/和/policy/single_recommend/
- 添加celery task，批量检查多个企业和单个指南匹配情况
- 添加json-rpc服务器，对外提供获取政策或指南文本的功能，封装JAVA实现的数据访问接口

### Changed

- 所有配置项都在config.ini中进行配置



##  [1.0.0] - 2018-12-20

### Added

- 实现两个政策指南的推荐