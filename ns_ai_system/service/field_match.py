# coding=utf-8
import warnings

from celery_task import log


class FieldMatcher():
    def __init__(self):
        self._field_match_route = dict()
        # self._default_match_funcs=[]

    def match_func(self, field_name):
        """通过修饰器的方式将字段判断函数与字段名相关联。
        判断函数接受三个参数
        field_info: {'Name':中文名, 'Field':字段名}
        query_data:
        spo:
        """

        def decorator(f):
            self._field_match_route[field_name] = f
            return f

        return decorator

    #
    # def default_match_func(self):
    #     def decorator(f):
    #         self._default_match_func=f

    def is_match(self, field_info, query_data, spo):
        """

        :param field_info: {'Name':中文名, 'Field':字段名}
        :param query_data:
        :param spo: {"subject": subject, "predicate": predicate, "object": object}
        :return: 如果没有匹配函数，则返回None；否则，返回是否满足条件，以及字段对应的值
        """
        subject, predicate, object = spo
        log.info(spo)
        if field_info is None:
            raise Exception("field_info is None")
        is_match_func = self._field_match_route.get(field_info["name"], None)
        if is_match_func is None:
            warnings.warn(
                f"Match function not found for {field_info['name']}. It won`t be shown in result and matching score.")
            return None
        else:
            match,data=is_match_func(field_info, query_data, {"subject": subject, "predicate": predicate, "object": object})
            reason=f"{subject['tag']}{predicate['tag'].replace('内','在')}{object['tag']}【{data}】"
            return match,reason

field_matcher = FieldMatcher()
from service.match_funcs.funcs import *
