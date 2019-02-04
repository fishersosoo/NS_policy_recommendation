# coding=utf-8

import unittest

import pymongo
import requests

py_client = pymongo.MongoClient(host="ns.fishersosoo.xyz", port=80, connect=False)
ai_system = py_client.ai_system

ai_system.recommend_record.remove({"guide_id":None})
def get_companies(guide_id="40"):
    companies = list(ai_system.recommend_record.distinct("company_id", {"guide_id": guide_id}))
    return companies


class TestCheckRecommend(unittest.TestCase):
    def setUp(self):
        self.json = {
            "companies": [],
            "guide_id": "40",
            "callback": "http://127.0.0.1:8002/callback/"
        }
        self.guide_id = "40"
        self.companies = get_companies(guide_id=self.guide_id)
        self.url = "http://ns.fishersosoo.xyz:3306/policy/check_recommend/"
        self.callback = "http://127.0.0.1:8002/callback/"

    # def test_no_company(self):
    #     print(__name__)
    #     self.json["companies"]=[]
    #     ret=requests.post(self.url,json=self.json)
    #     self.assertEqual(ret.ok,True)
    #     print(ret.content)

    def test_not_full(self):
        print(__name__)
        self.json["companies"]=self.companies[:1]
        ret=requests.post(self.url,json=self.json)
        self.assertEqual(ret.ok,True)
        print(ret.content)

    # def test_full(self):
    #     print(__name__)
    #     self.json["companies"]=self.companies[:12]
    #     ret=requests.post(self.url,json=self.json)
    #     self.assertEqual(ret.ok,True)
    #     print(ret.content)


#
# if __name__ == '__main__':
#     print(get_companies())
