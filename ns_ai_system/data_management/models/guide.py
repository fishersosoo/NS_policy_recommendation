# coding=utf-8
import datetime
from collections import defaultdict
from mimetypes import guess_type

import gridfs
from bson import ObjectId
from py2neo import Node, Relationship, NodeMatcher, Subgraph

from data_management.config import py_client
from data_management.models import BaseInterface, UUID, graph_
from data_management.models.policy import Policy


class Guide(BaseInterface):
    @classmethod
    def parsing_info(self, guide_id):
        ret = py_client.ai_system["parsing_result"].find_one({"guide_id": guide_id})
        if ret is not None:
            return ret
        else:
            return defaultdict(str)

    @classmethod
    def get_file(cls, guide_id):
        """
        获取指南文件
        Args:
            guide_id: 指南id

        Returns:
            GridOut对象
        """
        ret = py_client.ai_system["guide_file"].find_one({"guide_id": guide_id})
        if ret is None:
            return None
        else:
            storage = gridfs.GridFS(py_client.ai_system, "guide_file")
            grid_out = storage.find_one({"_id": ret["file_id"]})
            if grid_out is None:
                return None
            else:
                return grid_out

    @classmethod
    def file_info(cls, file_id):
        """

        Args:
            file_id:

        Returns:

        """
        storage = gridfs.GridFS(py_client.ai_system, "guide_file")
        ret = storage.find_one({"_id": file_id})
        if ret is None:
            return defaultdict(str)
        else:
            return {"uploadDate": ret.uploadDate, "filename": ret.filename, "contentType": ret.contentType}

    @classmethod
    def list_guide(cls):
        """

        Returns:
        返回所有指南记录列表

        """
        return list(py_client.ai_system["guide_file"].find({}))

    @classmethod
    def list_valid_guides(cls):
        """
        查找所有在有效日期内的指南
        :rtype: list[Node]
        :return: 指南节点
        """
        return list(py_client.ai_system["guide_file"].find({"effective": {"$ne": False}}))

    @classmethod
    def create(cls, guide_id, file_name, fileobj, base="guide_file", **kwargs):
        """
        保存指南id以及指南文件到mongo数据库

        Args:
            guide_id: 指南id
            file_name: 保存的文件名
            fileobj: 已经打开的fileobj
            base: 保存到mongo数据库表名
            **kwargs: 其他需要保存的信息

        Returns:

        """
        if not (hasattr(fileobj, "read") and callable(fileobj.read)):
            raise TypeError("'fileobj' must have read() method")
        content_type, _ = guess_type(file_name)
        storage = gridfs.GridFS(py_client.ai_system, base)
        # 检查是否有旧纪录，如果有删除对应的文件
        old_rets = list(py_client.ai_system["guide_file"].find({"guide_id": guide_id}))
        for one in old_rets:
            storage.delete(one["file_id"])
        # 插入或更新数据
        py_client.ai_system["guide_file"].update_one({"guide_id": guide_id},
                                                     {"$set": {"file_name": file_name, "guide_id": guide_id}},
                                                     upsert=True)
        file_id = storage.put(fileobj, filename=file_name, content_type=content_type)
        record = {"file_name": file_name, "guide_id": guide_id,
                  "file_id": file_id}
        record.update(kwargs)
        py_client.ai_system["guide_file"].update_one({"guide_id": guide_id},
                                                     {"$set": record},
                                                     upsert=True)


if __name__ == '__main__':
    print(Guide.list_valid_guides())
