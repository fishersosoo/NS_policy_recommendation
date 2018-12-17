# 智能平台api说明

最后更新：2018年12月5日

## /policy/upload_policy/

上传政策文件

### POST

form-data

| key       | value    |
| --------- | -------- |
| file      | 政策文件 |
| policy_id | 政策id   |

政策文件格式需求：

目前可支持的格式如下

txt:要求以UTF-8编码txt

doc:要求以UTF-8编码doc（仅doc中的文字内容会被识别）

## /policy/upload_guide/

### POST

上传指南文件，并将指南文件和对应的的事项以及政策相（系统会对指南文件进行理解）

form-data

输入：

| key       | value            |
| --------- | ---------------- |
| file      | 指南文件         |
| guide_id  | 指南文件id       |
| policy_id | 指南依据的政策id |

指南文件格式需求：

目前可支持的格式如下

doc:要求以UTF-8编码doc

输返回：

```json
{
    status: "状态"
    message:"和状态相关的扩展提示，例如指明失败原因是因为文件格式不支持等"
}
```

## /policy/recommend/

### GET

获取给该企业推荐的事项。

/policy/recommend/?company_id=123

使用company_id进行查询的时候，系统首先会将提交一个异步任务到后台，重新计算对该企业推荐哪些政策，异步任务的id放入返回内容中的`task_id`字段中。查找是否存在这个企业的历史推荐记录，历史记录会放入到返回内容中的`result`字段中，若不存在历史推荐记录，则`result`为一个空的列表。

`matching`表示推荐的结果和企业的匹配程度，例如，推荐的指南有10个条件，企业满足9个，则`matching`为0.9。

`reason`是字符串，表示推荐的原因。会列出指南中企业满足的条件。这些条件不一定是原文，但是在语义上一致。

`matching`和`reason`是在推荐记录生成，也就是`time`计算出来的。当企业信息发生变化之后这些信息不会在本记录上改变，但是会反映在新的推荐记录上。

> 例如，在2018-11-01推荐了**事项1**，匹配度是0.7则会有一条` {"guide_id": "01", "matching" : 0.70, "time": "2018-11-01 00:00:01"}`的记录。在一个月之后，企业数据发生变化，对于**事项1**的匹配度变为0.9，则上述记录还会保留，但是会增加一条`{"guide_id": "01", "matching" : 0.90, "time": "2018-12-01 00:00:01"}`的记录。

```json
{
    "task_id": "异步任务id，可以用于更新推荐的政策",
    "result": [
        {
            "guide_id": "推荐事项的id",
            "reason": "推荐原因，可用于展示",
            "matching" : 0.90, 
            "time": "推荐时间，fmt:YYYY-MM-DD HH:mm:ss"
        },
        {}
    ]
}
```

/policy/recommend/?task_id=123

使用company_id进行查询后，可以使用拿到的task_id获取更新后的企业推荐记录。

```json
{
    "status": "任务状态",
    "result": [
        {
            "policy_id": "推荐的政策id",
            "reason": "推荐原因",
            "time": "推荐时间，fmt:YYYY-MM-DD"
        },
        {}
    ]
}
```

