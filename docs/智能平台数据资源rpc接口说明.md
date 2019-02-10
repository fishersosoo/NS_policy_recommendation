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

