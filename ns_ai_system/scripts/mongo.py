#coding=utf-8
import json

import pymongo
import requests

py_client = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80, connect=False)
ai_system = py_client.ai_system
f=open(r"C:\Users\fishe\Documents\Tencent Files\985175863\FileRecv\result (2).json")
d=json.load(f)

ai_system.parsing_result.insert_one({"guide_id":"111", "triples": d})