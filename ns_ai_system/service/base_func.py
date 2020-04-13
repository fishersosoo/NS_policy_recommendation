# coding=utf-8
import datetime
import copy

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

def match_with_labels(recommend_record_no_label, labels):
    """
    使用标签对异步计算的结果进行调整
    Args:
        recommend_record_no_label: 单个异步计算结果
        labels: 标签列表.[{"_id":"","text":""}]

    Returns:
       recommend_record_with_label.和recommend_record_no_label结果相似，多了label字段

        {
        "company_id": "",
        "label":["",],
        "guide_id": "",
        "time": datetime.datetime.utcnow(),
        "latest": True,
        "has_label": False,
        "sentences": [
            {
                "text":"",
                "type": "正常",
                "result": "",
                "clauses":[
                    {
                        "fields":["专利名称",],
                        "relation":"是",
                        "value":"规定航运物流",
                        "result":"mismatch"
                    },
                ]
            }
        ]
    }

       labels.每个label增加了match_count表示匹配了多少个条件
       [
       {"_id":"",
       "text":"",
       "match_count":0,},
       ]
    """
    labels_with_match_count = copy.deepcopy(labels)
    recommend_record_with_label = copy.deepcopy(recommend_record_no_label)
    recommend_record_with_label["has_label"] = True
    recommend_record_with_label["label"] = []
    for sentence in recommend_record_with_label["sentences"]:
        if sentence["type"] != "正常" and len(sentence["clauses"]) != 0:
            continue
        for clause in sentence["clauses"]:
            if clause["result"] != "match" and clause.get("value", None) is not None:
                for label in labels_with_match_count:
                    is_match = is_match_label(clause["value"], label)
                    if is_match:
                        clause["result"] = "match"
                        sentence["result"] = "match"
                        if "match_count" not in label:
                            label["match_count"] = 1
                        else:
                            label["match_count"] += 1
    for label in labels_with_match_count:
        if label.get("match_count", 0) != 0:
            recommend_record_with_label["label"].append(label["text"])
    return recommend_record_with_label, labels_with_match_count

def is_match_label(value, label):
    """

    Args:
        label: {"_id":"","text":""}
        value: "政策文本"

    Returns:
        bool. 标签和文本是否匹配
    """
    if type(value) == list:
        for v in value:
            if label["text"] in v:
                return True
        return False
    else:
        return label["text"] in value