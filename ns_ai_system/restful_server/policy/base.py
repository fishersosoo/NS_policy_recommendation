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
    except Exception as e:
        stack = traceback.extract_stack()
        pass
    finally:
        return is_ok, stack
