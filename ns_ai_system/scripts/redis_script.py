# coding=utf-8
import redis
import json

if __name__ == '__main__':
    pool = redis.ConnectionPool(host='localhost', port=8000, decode_responses=True, db=1)
    r = redis.Redis(connection_pool=pool)
    keys = r.keys()
    r.set_response_callback("MGET", lambda l: [eval(i) for i in l])
    ret = r.mget(keys[0], keys[1])
    print(type(ret[1][1]))
    print(ret[1][1])
