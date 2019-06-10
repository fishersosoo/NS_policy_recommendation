# coding=utf-8
import json
import time

import requests
from bson import ObjectId

from data_management.config import py_client
from data_management.models.guide import Guide
from data_management.models.policy import Policy
from data_server.server import jsonrpc, mongo, max_seq, tokenizer, client, uid
from model.bert_vec.data_processing import convert_to_ids
from service.file_processing import get_text_from_doc_bytes
from service.rabbit_mq import file_event

from bert_serving.client import BertClient

from read_config import ConfigLoader

config = ConfigLoader()


@jsonrpc.method("api.index")
def index():
    return "index"


@jsonrpc.method('guide.list_guide_id')
def list_guide_id():
    """
    返回所有指南id

    Returns:

    """
    return [one["guide_id"] for one in list(py_client.ai_system["guide_file"].find())]


@jsonrpc.method("file.register")
def register(url, use, id=None):
    """
    注册回调函数，之后文件发生的变化将会通过该回调函数进行通知
    :param use: 用于备注用途
    :param url: 回调函数地址（完整地址）
    :param id: （可选）如id不为None则会修改对应id的回调函数地址，建立新的回调
    :return: 返回id用于修改回调函数地址
    """
    func = {"url": url, "use": use}
    if id is None:
        mongo.db.register.insert_one(func)
        return str(func["_id"])
    else:
        result = mongo.db.register.update({"_id": ObjectId(id)},
                                          {"$set": func}, upsert=False, multi=True)
        return str(result['nModified'] == 1)


@jsonrpc.method("file.get_policy_text")
def get_policy_text(policy_id):
    """
    获取政策文本\n
    :param policy_id: 平台政策id\n
    :return:
    """
    _, _, policy_node = Policy.find_by_policy_id(policy_id)
    text = get_text_from_doc_bytes(Policy.get_file(policy_node["file_name"]).read())
    return text


@jsonrpc.method("file.get_guide_text")
def get_guide_text(guide_id):
    """
    获取指南文本
    :param guide_id:
    :return:
    """
    _, _, guide_node = Guide.find_by_guide_id(guide_id)
    text = get_text_from_doc_bytes(Guide.get_file(guide_node["file_name"]).read())
    return text


@jsonrpc.method('test.upload_guide')
def test_upload_guide(guide_id):
    file_event(message=json.dumps({"guide_id": guide_id, "event": "add"}), routing_key="event.file.add")


@jsonrpc.method('data.sendRequest')
def sendRequest(comp_id, params):
    """
    调用通用接口获取数据
    :param service_name: 接口名称
    :param params: 查询参数
    :return:
    """
    value = client.service.getParamInfo(uid, comp_id, params)._value_1
    value = json.loads(value)
    print(params)
    if value["Status"] == "Success":
        result = value["Result"]
        return [list(one.values())[0] for one in result]
    else:
        return None


@jsonrpc.method("model.bert_word2vec")
def bert_word2vec(strs):
    """
    使用bert模型进行char level的 word2vec

    :param strs: [str]. 多个str
    :return:
    list, shape:[len(strs), 32, 768]

    """
    if isinstance(strs, str):
        strs = [strs]
    start_time = time.time()
    bc = BertClient(ip=config.get('bert', 'ip'))
    return bc.encode(strs).tolist()
