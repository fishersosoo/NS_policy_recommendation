# coding=utf-8

from data_management.config import  dataService

if __name__ == '__main__':
    params = dict()
    params.__setitem__("entName", "广州紫川电子科技有限公司")
    params.__setitem__("pageNo", 1)
    params.__setitem__("pageSize", 200000000000000)
    # print(dataService.sendRequest("getEntByKeyword", {"keyword":  "广州紫川电子科技有限公司","type":0})["RESULTDATA"][0])
    # params.__setitem__("type", 0)
    value = dataService.sendRequest("getQualifyCertifyInfo", params)
    for one in value["RESULTDATA"]:
        result=one
        for k,v in result.items():
            if k=="FQZ_ZZMC":
                print(k,v)
    result=value["PAGEINFO"]["TOTAL_COUNT"]
    print("_________________")
    # for k,v in result.items():
    #     print(k,v)
    # print(value)
    # print(py_client.ai_system["recommend_record"].update({"company_id": "91440101717852200L",
    #                                                 "guide_id": "13"},
    #                                                {"$set": {"latest": False}},upsert=False, multi=True))
    # print([one for one in py_client.ai_system["recommend_record"].find({"company_id": "91440101717852200L",
    #                                                 "guide_id": "40"})])
    # exit(-1)
