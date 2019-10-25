# 智能平台api说明

最后更新：2019年4月10日

更新记录

| 时间      | 内容                                                         |
| --------- | ------------------------------------------------------------ |
| 2019-4-10 | 修改/policy/check_recommend/和/policy/recommend/接口，增加threshold字段用于筛选返回记录 |
| 2019-1-4  | 增加/policy/check_recommend/和/policy/single_recommend/接口  |
| 2019-7-12 | 增加/policy/guides/接口                                      |
| 2019-7-19 | 修改推荐记录返回                                             |
| 2019-7-21 | 使用任务队列取代推送接口                                     |
| 2019-7-24 | 删除政策推送接口、上传政策文件接口                           |

## 说明

政策推送的接口用`rabbitmq`取代了。不同的队列对应不同的功能。`routing_key`为`task.single.input`的队列是用于政策推送的；`routing_key`为`task.multi.input`的队列是用于新企业注册之后的预计算。后者计算量是前者的几百倍，所以**不要把`task.multi.input`用作政策推送！！！**

政策推送的返回结果只有匹配度，需要根据匹配度过滤结果，使用`/policy/single_recommend/`来获取具体的条件。

`/policy/recommend/`接口适用于前端触发展示匹配结果时候使用

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

### POST

获取给该企业推荐的事项。

数据以json形式提供

`company_id`字段填入企业id。`label`列表为企业所拥有的标签，标签分为两种：标准标签库中的标签（通过`_id`来提供）、企业自填的标签（通过`text`来提供）。

样例如下：

```json
{
    "company_id": "企业id",
    "label": [
        {
            "_id": "id_1"
        },
        {
            "_id": "id_2"
        },
        {
            "text": "制药企业"
        }
    ]
}
```



返回的json形式的结果

结果返回到`result`字段所保存的列表中

列表中每一项表示一个政策和该企业的匹配情况，形式如下

- `label`字段存放和政策匹配的企业标签列表
- `match`字段存放部分匹配的条件及各自的匹配度`score`，至少有一个子条件满足的条件都会放在这里，具体请根据匹配度`score`进行判断
- `mismatch`字段存放完全不匹配的条件
- `unrecognized`字段存放未识别条件
- `score`字段存放整体政策匹配度，仅用于对返回的多个政策

**注意，在计算条件匹配情况时候已经将企业标签纳入计算中，返回结果中的`label`只是方便前端展示**

```json
{
    "_id": "5da989d9cbd02963add9218e",
    "company_id": "91440101668125196C",
    "guide_id": "220",
    "latest": true,
    "label":["匹配的企业标签1","匹配的企业标签2"],
    "match": [
        {
            "score": 0.5,
            "sentence": "部分匹配的条件1"
        },
        {
            "score": 0.5,
            "sentence": "部分匹配的条件2"
        }
    ],
    "mismatch": [
        {
            "sentence": "不匹配的条件1"
        },
        {
            "sentence": "不匹配的条件2"
        }
    ],
    "score": 0.5,
    "time": "Fri, 18 Oct 2019 09:46:01 GMT",
    "unrecognized": [        
        {
            "sentence": "未识别条件1"
        }]
}
```



## /policy/single_recommend/

### GET

获取某个企业和某个政策的最近一次匹配情况。本接口只进行数据的查询，不会重新计算匹配情况。（在调用`/policy/check_recommend/`之后，得到callback响应之后，可以根据匹配度是否满足情况再通过本接口获取具体推荐原因）

输入：

| key        | value  |
| ---------- | ------ |
| guide_id   | 指南id |
| company_id | 企业id |
|            |        |

输出：

json格式

```json
{
            "_id": "5d302f84cbd02966d9a23a0e",
            "company_id": "91440101668125196C",
            "guide_id": "220",
            "latest": true,
            "match": [
                { "sentence": "满足条件1" },
                { "sentence": "满足条件2" }
            ],
            "mismatch": [
                "不满足条件1",
                "不满足条件2"
            ],
            "score": 0.5,
            "time": "Thu, 18 Jul 2019 08:36:20 GMT",
            "unrecognized": [
                "未识别条件1",
                "未识别条件2"
            ]
}
```

## /policy/set_guide/

设置指南信息

### POST

以json格式编码

```json
{
	"guide_id":"指南id",
	"effective":true	
}
```

`effective`字段表示将指南设置为有效还是无效。当指南从有效变为无效的时候，该指南不再出现在返回结果中；当指南从无效变为有效的时候，后台重新计算该指南的匹配结果后再返回的匹配结果才是最新的。

## /policy/guide_file/

获取指南文件

输入：（编码到 URL 中）

| key      | value  |
| -------- | ------ |
| guide_id | 指南id |
|          |        |

## /policy/guides/

获取已经上传的文件的保存情况

返回字段含义

| key                | 含义                                                |
| ------------------ | --------------------------------------------------- |
| guide_id           | 指南id                                              |
| effective          | 是否有效                                            |
| contentType        | 文件类型                                            |
| filename           | 文件名                                              |
| uploadDate         | 上传时间                                            |
| doneDate           | 理解完成时间                                        |
| processAfterUpload | 理解完成-上传时间，负数表示上次上传之后理解还没完成 |

样例

```json
[
    {
        "contentType": "application/msword",
        "doneDate": "2019-07-12 17:06:10.084000+08:00",
        "effective": true,
        "filename": "114-1529981551435.doc",
        "guide_id": "114",
        "processAfterUpload": "0:01:04.033000",
        "uploadDate": "2019-07-12 17:05:06.051000+08:00"
    },
    {
        "contentType": "application/pdf",
        "doneDate": "None",
        "effective": true,
        "filename": "Dynamic Resource Management Using.pdf",
        "guide_id": "115",
        "processAfterUpload": "政策未理解",
        "uploadDate": "2019-07-12 16:43:49.568000+08:00"
    }
]
```



## 企业标签

### /label/list/

GET

获取标签库所有标签，以json形式返回

```json
[
    {"_id":"标签id","text":"标签"},
    {"_id":"标签id","text":"标签"}
]
```



### /label/edit/

POST

修改标签库某个标签。

以json形式输入参数

以下参数会将标签id对应的标签文本修改为”标签a“。如果没有`_id`字段则会尝试往标签库中添加”标签a“（重复则不添加）。

```json
{"_id":"标签id","text":"标签a"}
```



### /label/delete/

删除标签库某个标签

POST

以json形式输入参数

```json
{"_id":"标签id"}
```





## 任务队列

端口、用户名、密码信息尚未确定。

政策推送任务通过rabbitMQ任务队列来进行输入输出信息的交换。

| 任务                   | 输入routing_key     | 输出队列              |
| ---------------------- | ------------------- | --------------------- |
| 单个企业和单个政策匹配 | `task.single.input` | `single_guide_result` |
| 单个企业和多个政策匹配 | `task.muilt.input`  | `multi_guide_result`  |



### 添加任务

如果进行单个企业和单个政策的匹配，则使用`task.single.input`作为routing_key，输入队列的信息形如`{"guide_id": guide_id, "company_id": company_id}`的序列化json。

如果进行单个企业和多个政策的匹配，则使用`task.muilt.input`作为routing_key，输入队列的信息形如`{"company_id": company_id}`的序列化json。

python例子如下：

```python
# coding=utf-8
# 添加任务的例子
import pika
import json

host = "127.0.0.1"
port = 8001
user = "guest"
pwd = "guest"

if __name__ == '__main__':
    # 初始化channel，channel请复用以减少带宽消耗
    credentials = pika.credentials.PlainCredentials(user, pwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host, port=port, virtual_host="/", credentials=credentials))
    channel = connection.channel()
    company_id = "企业id"
    guide_id = "指南id"
    message = json.dumps({"guide_id": guide_id, "company_id": company_id})  # 需要序列化成json字符串
    channel.basic_publish(exchange='task', routing_key='task.single.input', body=message)
```

### 获取结果

获取结果需要为特定队列绑定一个回调函数，在回调函数处理队列中的消息。

如果进行单个企业和单个政策的匹配，则结果队列为`single_guide_result`，队列的信息形如`{"guide_id": guide_id, "company_id": company_id,"score":0.1}`的序列化json。

如果进行单个企业和多个政策的匹配，则结果队列为`multi_guide_result`，队列的信息如下的序列化json。

```json
{"guide_id": guide_id, "company_id": company_id,"score":0.1}
```



python例子如下

```python
# coding=utf-8
import json
import pika

host = "127.0.0.1"
port = 8001
user = "guest"
pwd = "guest"

def single_result_callback(channel, method, properties, message):
    """
    从队列中取出一个消息之后的回调函数，在这个函数内处理返回结果
    """
    print(f"{channel}\n{method}\n{properties}\n{message}")
    print("____________________")

if __name__ == '__main__':
    credentials = pika.credentials.PlainCredentials(user, pwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host, port=port, virtual_host="/", credentials=credentials))
    channel = connection.channel()
    channel.basic_consume(on_message_callback=single_result_callback, queue="single_guide_result", auto_ack=True)	# 将回调函数绑定到队列上。auto_ack=True，否则队列中的消息会一直存在。
    channel.start_consuming()	# 线程会阻塞

```

