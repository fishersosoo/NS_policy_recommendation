#coding=utf-8

import pymongo
import requests

py_client = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80, connect=False)
ai_system = py_client.ai_system

ai_system.recommend_record.remove({"guide_id":None})