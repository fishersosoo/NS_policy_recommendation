# coding=utf-8
"""
数据库访问配置
"""

import pymongo

from data_management.data_service_proxy import DataService
from read_config import ConfigLoader
import redis

config = ConfigLoader()
pool = redis.ConnectionPool(host=config.get('cache_redis', 'host'), port=int(config.get('cache_redis', 'port')),
                            decode_responses=True, db=int(config.get('cache_redis', 'db')))
redis_cache = redis.Redis(connection_pool=pool)
redis_cache.set_response_callback("MGET", lambda l: [eval(i) if i is not None else None for i in l])
neo4j_config = config._config['neo4j']
py_client = pymongo.MongoClient(host=config.get('mongoDB', 'host'), port=int(config.get('mongoDB', 'port')),
                                connect=False)
dataService = DataService(url=f"http://{config.get('data_server','host')}:{config.get('data_server','port')}/data")

if __name__ == '__main__':
    value = dataService.sendRequest("getEntByKeyword", {"keyword": "91110108740053589U", "type": 1})
    print(value)
