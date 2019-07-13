# coding=utf-8
import csv
import datetime
import os

from data_management.config import py_client


def load_recommend_record_from_csv(csv_path):
    guide_id = os.path.splitext(os.path.split(csv_path)[1])[0]
    with open(csv_path, encoding='utf-8') as csv_file:
        csv_data = csv.DictReader(csv_file)
        for row in csv_data:
            record = dict(guide_id=guide_id, time=datetime.datetime.utcnow(), latest=True)
            reasons = ["企业满足以下条件：【括号中内容为企业的真实情况】"]
            matched_count = 0
            requirement_count = 0
            for k, v in row.items():
                if "社会信用号" in k:
                    record["company_id"] = v
                elif k != "企业名称":
                    requirement = k
                    requirement_count += 1
                    if v != "":
                        matched_count += 1
                        reason = f"{matched_count}. {requirement}【{v}】"
                        reasons.append(reason)
            matching = matched_count / requirement_count
            record["reason"] = "\n".join(reasons)
            if guide_id == "13":
                matching += 0.25
            else:
                matching += 0.1
            record["matching"] = matching
            if matching > 0:
                py_client.ai_system["recommend_record"].insert_one(record)


if __name__ == '__main__':
    load_recommend_record_from_csv(
        r"Y:\Nansha AI Services\condition_identification\ns_ai_system\res\recommend_record\40.csv")
    load_recommend_record_from_csv(
        r"Y:\Nansha AI Services\condition_identification\ns_ai_system\res\recommend_record\13.csv")
    # mongodb[]
