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
