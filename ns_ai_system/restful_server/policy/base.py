# coding=utf-8
import traceback
from random import random

import requests


def check_callback(url, guide_id):
    """
    检查callback是否是否正确
    :param url: callback的url
    :param guide_id: 指南id
    :return: bool,表示callback是否正确
    """
    rand_num = round(random(), 2)
    is_ok = False
    stack = ""
    try:
        ret = requests.post(url, json={
            "guide_id": "指南id",
            "task_id": "test",
            "result": {
                "test": {"matching": rand_num, "status": "TEST"}
            }
        })
        if ret.ok and float(ret.content) == rand_num:
            is_ok = True
            stack="content not match"
    except Exception as e:
        stack ="can not resolve url"
        pass
    finally:
        return is_ok, stack

def check_contains(guide_id, guide_lists):
    """
    检查guide_id是否在guide_lists中
    :param guide_id:政策的id
    :param guide_lists: 政策的列表，是一个字典列表
    :return dict, is_contain bool值，表示是否包含，guide，表示政策
    """
    result = dict()
    result['is_contain'] = False
    for one in guide_lists:
        if guide_id == one['guide_id'] :
            result['guide'] = one
            result['is_contain'] = True
    return result