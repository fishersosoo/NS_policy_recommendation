# coding=utf-8
"""访问neo4j数据库"""
from neo4j.v1 import GraphDatabase


class Neo4jInterface():
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()


if __name__ == "__main__":
    c = Neo4jInterface("bolt://cn.fishersosoo.xyz:7687", "neo4j", "1995")
    c.close()
