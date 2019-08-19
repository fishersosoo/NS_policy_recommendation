# coding=utf-8
import datetime
import json

import gridfs
import pymongo
import requests
from bson import ObjectId

import csv

from data_management.models.guide import Guide

py_client = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80, connect=False)
ai_system = py_client.ai_system


def download_field_value():
    all_data = list(ai_system.field_value.find({}))
    field_set = dict()
    for one in all_data:
        name = f"{one['resource_id']}.{one['item_id']}"
        if name not in field_set:
            field_set[name] = set(one["value"])
        else:
            field_set[name].add(one["value"])
    field_list = dict()
    for name, value_set in field_set.items():
        field_list[name] = list(value_set)
    with open('/data/NS_policy_recommendation/field_set.json', 'w') as f:
        json.dump(field_list, f)
    with  open('/data/NS_policy_recommendation/field_count.csv', 'w') as f:
        witer = csv.writer(f)
        for k, v in field_set.items():
            witer.writerow([str(k), str(len(v))])


if __name__ == '__main__':
    # Guide.delete_guide("422")
    Guide.delete_guide("420")
    # Guide.delete_guide("424")

    # industry_list = list(ai_system.field_value.distinct("value", {"resource_id": "DR1", "item_id": "INDUSTRY"}))  # 领域列表
