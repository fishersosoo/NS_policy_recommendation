# 智能平台数据资源rpc接口说明

智能平台中的文件和数据暴露rpc接口对外提供数据。

## rpc访问

使用json-rpc进行访问

使用POST方法进行访问，地址为 http://{host}/data

访问时候header必须设置`"Content-Type":"application/json"`

将以下信息填入到body中

```json
{
    "jsonrpc": "2.0",
    "method": "file.get_guide_text",# 方法名称
    "params": {		# 具体参数
      "guide_id": "40"
    },
    "id": "6f7b3dc8-6162-4af4-a182-6af21b3b787f"
  }
```

返回的信息如下

```json
{
  "id": "6f7b3dc8-6162-4af4-a182-6af21b3b787f",
  "jsonrpc": "2.0",
  "result": "" 			# 实际的返回内容
}
```



可以访问http://{host}/data/browse/ 浏览api

python访问demo脚本：

https://github.com/fishersosoo/NS_policy_recommendation/tree/feature/tests/data_server_demo.py

## rpc方法列表

### file.get_guide_text(guide_id: str) -> str

获取指南字符串

方法名称:file.get_guide_text

输入：

| 参数     | 类型 | 备注   |
| -------- | ---- | ------ |
| guide_id | str  | 指南id |

返回：

对应指南文件中的字符串

### file.get_policy_text(policy_id: str) -> str

获取政策字符串

方法名称:file.get_policy_text

输入：

| 参数      | 类型 | 备注   |
| --------- | ---- | ------ |
| policy_id | str  | 政策id |

返回：

对应政策文件中的的字符串

### guide.list_guide_id() -> list[str]

获取所有指南id

方法名称:guide.list_guide_id

返回：

指南id列表

## 消息队列相关

基于rabbitmq实现文件相关事件的发布

测试服务器上连接rabbitmq参数：

```ini
host=127.0.0.1
port=8001
user=guest
pwd=guest
```

问答和全文检索系统对应的队列为`file_event_qa`和`file_evnet_query`

返回的消息以`json`方式编码，格式如下

```json
{
    "guide_id":"123",
    "event":"add"
}
```

目前`event`类型：

| event   | 意义       |
| ------- | ---------- |
| add     | 添加指南   |
| disable | 标记为无效 |
| enable  | 标记为有效 |

rpc接口提供以下方法供测试消费者函数是否正确：

**test.upload_guide(guide_id: str) -> any**

调用该方法会将向队列中添加该指南文件被添加的消息。（但是实际没有文件上传，所以不能调用上面接口来获取文件内容）