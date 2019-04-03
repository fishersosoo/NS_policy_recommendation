# coding=utf-8
import datetime

from celery_task import log
from condition_identification.api.text_parsing import triple_extract, paragraph_extract
from data_management.config import py_client
from data_management.models.guide import Guide
from service.file_processing import get_text_from_doc_bytes


def understand_guide(guide_id,text):
    """
    理解指定政策指南

    :param guide_id:指南节点的外部id
    :return:
    """
    # print(guide_id)
    # _, _, guide_node = Guide.find_by_guide_id(guide_id)
    # text = get_text_from_doc_bytes(Guide.get_file(guide_node["file_name"]).read())
    print(text[:100])
    triples = triple_extract(paragraph_extract(text))
    py_client.ai_system["parsing_result"].insert_one({"guide_id": guide_id, "triples": triples})
    print("done")




