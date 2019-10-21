# coding=utf-8

from flask_restful import Api
from flask import jsonify, request

from data_management.models.label import Label
from restful_server.label import label_service
from restful_server.server import mongo


@label_service.route("list/", methods=["GET"])
def list_label():
    """
    返回所有标签
    Returns:

    """
    labels = Label.list_label()
    return jsonify(labels)


@label_service.route("edit/", methods=["POST"])
def edit_label():
    """
    修改标签。输入_id和text字段
    如无_id字段或没有对应_id的标签，则尝试创建
    Returns:
        {
            "n": 0,
            "nModified": 0,
            "ok": 0,
        }
        或新标签的id
    """
    params = request.json
    text = params.get("text", None)
    if text is None:
        return jsonify({
            "n": 0,
            "nModified": 0,
            "ok": 0,
        })
    id = params.get("_id", "")
    return jsonify(Label.edit_label(id, text))

@label_service.route("delete/",methods=["POST"])
def delete_label():
    """
    根据id删除标签
    Returns:

    """
    params = request.json
    _id = params.get("_id", "")
    return Label.delelte_label(_id)