# encoding=utf-8
from bson import ObjectId

from data_management.config import py_client


class Label:
    @classmethod
    def convert_texts(cls, labels):
        """
        将列表里面的id转为对应的text
        Args:
            labels:

        Returns:
            [{"_id":"id-1","text":"label-1"},{"_id":"id-2","text":"label-2"}]
        """
        ret = []
        for label in labels:
            if "_id" in label:
                oid = None
                try:
                    oid = ObjectId(label["_id"])
                except Exception as e:
                    pass
                if oid is None:
                    continue
                else:
                    one = py_client.ai_system["label"].find_one({"_id": oid})
                    if one is not None:
                        label["text"] = one["text"]
                        ret.append(label)
            elif "text" in label:
                oid = py_client.ai_system["label"].find_one({"text": label["text"]})
                if oid is not None:
                    label["_id"] = str(oid["_id"])
                ret.append(label)
        return ret

    @classmethod
    def add_label(cls, text):
        """
        添加标签。如有重复则不会添加
        Args:
            text:

        Returns:

        """
        return py_client.ai_system["label"].update_one({"text": text},
                                                       {"$set": {"text": text}},
                                                       upsert=True).upserted_id

    @classmethod
    def edit_label(cls, _id, text):
        """
        修改标签，如id不存在则尝试添加
        Args:
            _id:
            text:

        Returns:
        {
            "n": 匹配的数量,
            "nModified": 修改数量,
            "ok": 0,
        }
        """
        update_result = py_client.ai_system["label"].update_one({"_id": ObjectId(_id)},
                                                                {"$set": {"text": text}},
                                                                upsert=False)
        if update_result.matched_count == 0 and update_result.matched_count == 0:
            return cls.add_label(text)
        else:
            return update_result.raw_result

    @classmethod
    def delelte_label(cls, _id):
        """
        删除某个标签
        Args:
            _id:

        Returns:

        """
        return py_client.ai_system["label"].delete_one({"_id": ObjectId(_id)}).raw_result

    @classmethod
    def list_label(cls):
        """
        返回标签列表
        Returns:

        """
        return list(py_client.ai_system["label"].find({}))
