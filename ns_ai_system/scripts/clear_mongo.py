# coding=utf-8
# coding=utf-8
import json

import gridfs
import pymongo
import requests

if __name__ == '__main__':
    py_client = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80, connect=False)
    ai_system = py_client.ai_system
    py_client.celery.celery_taskmeta.delete_many({})
    py_client.ai_system.parsing_result.delete_many({})
    py_client.ai_system.recommend_record.delete_many({})
    py_client.ai_system.guide_file.delete_many({})
    storage = gridfs.GridFS(py_client.ai_system, "guide_file")
    for grid_out in storage.find({},
                                 no_cursor_timeout=True):
        storage.delete(grid_out._id)
