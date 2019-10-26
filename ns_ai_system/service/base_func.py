# coding=utf-8
import datetime

from data_management.config import py_client
from data_management.models.guide import Guide


def is_expired(recommend_record, expired=None):
    """
    一个推荐记录是否超时
    Args:
        recommend_record: 推荐记录
        expired: 超时时间

    Returns:

    """
    if expired is None:
        expired = py_client.ai_system["config"].find_one({"recommend_expired_hours": {'$exists': True}})[
            "recommend_expired_hours"]
        expired = float(expired)
        expired = datetime.timedelta(hours=expired)
    # print(recommend_record['time'])
    if expired < datetime.datetime.now(datetime.timezone.utc) - recommend_record['time']:
        return True
    else:
        return False


def get_needed_check_guides(company_id, expired=None, recommend_records=None):
    """
    获取需要计算的政策id

    Args:
        company_id: 企业id
        expired:超时小时

    Returns:
        需要计算的政策id集合
    """
    if expired is None:
        expired = py_client.ai_system["config"].find_one({"recommend_expired_hours": {'$exists': True}})[
            "recommend_expired_hours"]
    expired = float(expired)
    expired = datetime.timedelta(hours=expired)
    valid_guides = [one["guide_id"] for one in Guide.list_valid_guides()]
    if recommend_records is None:
        recommend_records = [one for one in py_client.ai_system["recommend_record"].find(
            {"company_id": company_id, "has_label": False, "guide_id": {"$in": valid_guides}, "latest": True})]
    needed_update = set(valid_guides) - {one["guide_id"] for one in recommend_records}
    for one in recommend_records:
        if is_expired(one, expired):
            needed_update.add(one["guide_id"])
    return needed_update

def format_record(one_result_with_label):
    """
    将数据格式化到输出形式
    Args:
        one_result_with_label:

    Returns:
         {
                "_id": "5da989d9cbd02963add9218e",
                "company_id": "91440101668125196C",
                "guide_id": "220",
                "latest": true,
                "label":["匹配的企业标签1","匹配的企业标签2"],
                "match": [
                    {
                        "score": 0.5,
                        "sentence": "部分匹配的条件1"
                    },
                    {
                        "score": 0.5,
                        "sentence": "部分匹配的条件2"
                    }
                ],
                "mismatch": [
                    {
                        "sentence": "不匹配的条件1"
                    },
                    {
                        "sentence": "不匹配的条件2"
                    }
                ],
                "score": 0.5,
                "time": "Fri, 18 Oct 2019 09:46:01 GMT",
                "unrecognized": [
                    {
                        "sentence": "未识别条件1"
                    }]
            }
    """
    ret = {
        "company_id": one_result_with_label["company_id"],
        "guide_id": one_result_with_label["guide_id"],
        "latest": True,
        "label": one_result_with_label.get("label",[]),
        "match": [],
        "mismatch": [],
        "unrecognized": [],
        "time": one_result_with_label["time"],
    }
    all_count = {"match": 0,
                 "mismatch": 0,
                 "unrecognized": 0}
    for sentence in one_result_with_label["sentences"]:
        if sentence["result"] == "unrecognized":
            ret["unrecognized"].append({"sentence": sentence["text"]})
        if sentence["result"] == "mismatch":
            ret["mismatch"].append({"sentence": sentence["text"]})
            all_count["mismatch"] += len(sentence["clauses"])
        if sentence["result"] == "match":
            # 计算条件匹配度
            count = {"match": 0,
                     "mismatch": 0,
                     "unrecognized": 0}
            for clause in sentence["clauses"]:
                result = clause.get("result", "unrecognized")
                count[result] += 1
                all_count[result] += 1
            ret["match"].append({
                "score": count["match"] / (count["match"] + count["mismatch"] + count["unrecognized"]),
                "sentence": sentence["text"]
            })
    ret["score"] = all_count["match"] / (all_count["match"] + all_count["mismatch"] + all_count["unrecognized"] + 1)
    return ret