# coding=utf-8
from service.field_match import field_matcher


@field_matcher.match_func("地址")
def DOM(field_info, query_data, spo):
    field = field_info["field"]
    data = query_data[field]
    is_match = spo["object"]["tag"] in data
    return is_match, data


@field_matcher.match_func("企业资质")
def FQZ_ZZMC(field_info, query_data, spo):
    field = field_info["field"]
    if spo["object"]["tag"] == "高新技术企业资质":
        spo["object"]["tag"] = "全国高新企业认证"
    data = query_data[field]
    is_match = spo["object"]["tag"] in data
    return is_match, data


@field_matcher.match_func("经营业务范围")
def OPSCOPE(field_info, query_data, spo):
    field = field_info["field"]
    data = query_data[field]
    is_match = False
    if "工业" in spo["object"]["tag"]:
        words = ["制造", "加工", "生产"]
        for word in words:
            if word in data:
                is_match = True
                continue
    return is_match, data


@field_matcher.match_func("行业领域")
def INDUSTRY(field_info, query_data, spo):
    field = field_info["field"]
    data = query_data[field]
    is_match = (spo["object"]["tag"] == data)
    return is_match, data


@field_matcher.match_func("企业类型")
def ENTTYPE(field_info, query_data, spo):
    field = field_info["field"]
    is_match = False
    data = query_data[field]
    if spo["object"]["tag"] == "独立法人资格":
        words = ["有限责任", "股份有限"]
        for word in words:
            if word in data:
                is_match = True
    return is_match, data
