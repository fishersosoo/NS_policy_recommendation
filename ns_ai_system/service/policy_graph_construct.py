# coding=utf-8
import datetime

from celery_task import log
from condition_identification.api.text_parsing import triple_extract, paragraph_extract
from data_management.config import py_client
from data_management.models.guide import Guide
from service.file_processing import get_text_from_doc_bytes


def understand_guide(guide_id, text):
    """
    理解指定政策指南

    :param guide_id:指南节点的外部id
    :return:
    """
    history = list(py_client.ai_system["parsing_result"].find({"guide_id": guide_id}))
    triples, _, sentences = triple_extract(paragraph_extract(text))
    py_client.ai_system["parsing_result"].insert_one(
        {"guide_id": guide_id, "triples": triples, "sentences": sentences, "doneTime": datetime.datetime.utcnow()})
    for one in history:
        py_client.ai_system["parsing_result"].delete_one({"_id": one["_id"]})
    log.info(f"{guide_id}:done!")
