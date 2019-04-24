#coding=utf-8
import json

import pymongo
import requests

py_client = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80, connect=False)
ai_system = py_client.ai_system
py_client.celery.celery_taskmeta.delete_many({})
# f=open(r"C:\Users\fishe\Documents\Tencent Files\985175863\FileRecv\0403\115.json")
# d=json.load(f)
#
# # py_client.ai_system["recommend_record"].update({"company_id": company_id,
# #                                                 "guide_id": guide_id},
# #                                                {"$set": {"latest": False}}, upsert=False, multi=True)
# ai_system.parsing_result.update({"guide_id":"115"},{"$set":{ "triples": d}},upsert=True)