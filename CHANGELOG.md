# 更新日志

此项目的所有显着更改都应记录在此文件中。

文件格式参照[如何维护更新日志](https://keepachangelog.com/zh-CN/1.0.0/)，本项目的版本号必须符合[语义化版本](https://semver.org/lang/zh-CN/)规范。

## [Unreleased]

### Added

- 添加restful接口，/policy/check_recommend/和/policy/single_recommend/
- 添加celery task，批量检查多个企业和单个指南匹配情况

### Deprecated

- 政策文件上传和访问的接口将会从restful server系统中移除，后续会建立新的独立文件系统



##  [1.0.0] - 2018-12-20

### Added

- 实现两个政策指南的推荐