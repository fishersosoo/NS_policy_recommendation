# coding=utf-8
import datetime
from mimetypes import guess_type

import gridfs
from py2neo import Node, Relationship, NodeMatcher, Subgraph

from data_management.config import py_client
from data_management.models import BaseInterface, UUID, graph_
from data_management.models.policy import Policy


class Guide(BaseInterface):

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
        py_client.ai_system["guide_file"].update_one({"guide_id": guide_id},
                                                        {"$set": {"file_name": file_name, "guide_id": guide_id}},
                                                        upsert=True)
        storage = gridfs.GridFS(py_client.ai_system, base)
        for grid_out in storage.find({"filename": file_name},
                                        no_cursor_timeout=True):
            storage.delete(grid_out._id)
        file_id = storage.put(fileobj, filename=file_name, content_type=content_type)
        record = {"file_name": file_name, "guide_id": guide_id,
                    "file_id": file_id}
        record.update(kwargs)
        py_client.ai_system["guide_file"].update_one({"guide_id": guide_id},
                                                        {"$set": record},
                                                        upsert=True)


if __name__ == '__main__':
    print(Guide.list_valid_guides())
