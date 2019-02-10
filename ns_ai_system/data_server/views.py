# coding=utf-8
from data_management.models.guide import Guide
from data_management.models.policy import Policy
from data_server.jvm_proxy import _attach_jvm_to_thread, DataServiceJavaProxy
from data_server.server import jsonrpc
from service.file_processing import get_text_from_doc_bytes


@jsonrpc.method("api.index")
def index():
    return "index"


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


@jsonrpc.method('data.sendRequest')
def sendRequest(service_name, params):
    """
    从调用龙信接口获取数据
    :param service_name: 接口名称
    :param params: 查询参数
    :return:
    """
    _attach_jvm_to_thread()
    return DataServiceJavaProxy.sendRequest(service_name, params)
