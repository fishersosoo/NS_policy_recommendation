# coding=utf-8
"""
数据库访问配置
"""
import datetime

import pymongo
import pytz

from data_management.data_service_proxy import DataService
import redis
from read_config import config

pool = redis.ConnectionPool(host=config.get('cache_redis', 'host'), port=int(config.get('cache_redis', 'port')),
                            decode_responses=True, db=int(config.get('cache_redis', 'db')))
redis_cache = redis.Redis(connection_pool=pool)
redis_cache.set_response_callback("MGET", lambda l: [eval(i) if i is not None else None for i in l])
neo4j_config = config._config['neo4j']
py_client = pymongo.MongoClient(host=config.get('mongoDB', 'host'), port=int(config.get('mongoDB', 'port')), tz_aware=True,tzinfo=pytz.timezone('Asia/Shanghai'),
                                connect=False)
dataService = DataService(url=f"http://{config.get('data_server','host')}:{config.get('data_server','port')}/data")

if __name__ == '__main__':
    t1= py_client.ai_system["recommend_record"].find_one({"company_id": "91440101668125196C", "guide_id": "220"})["time"]
    print(datetime.datetime.now(datetime.timezone.utc))
    print(t1)
    print(datetime.datetime.now(datetime.timezone.utc) -   t1       )