# coding=utf-8
import datetime

from celery_task import log
from condition_identification.api.text_parsing import triple_extract, paragraph_extract, Document
from data_management.config import py_client
from data_management.models.guide import Guide
from service.file_processing import get_text_from_doc_bytes


def filter_sentences(sentences):
    """
    过滤空的句子

    Args:
        sentences:
    """
    ids = list(sentences.keys())
    for id in ids:
        if len(sentences[id].strip()) < 2:
            sentences.pop(id)
    return sentences


def understand_guide(guide_id, text):
    """
    理解指定政策指南

    :param guide_id:指南节点的外部id
    :return:
    """
    history = list(py_client.ai_system["parsing_result"].find({"guide_id": guide_id}))
    document = Document.paragraph_extract(text)
    document.triple_extract()
    py_client.ai_system["parsing_result"].insert_one(
        {"guide_id": guide_id, "document": document.to_dict(),
         "doneTime": datetime.datetime.utcnow()})
    for one in history:
        py_client.ai_system["parsing_result"].delete_one({"_id": one["_id"]})
    log.info(f"{guide_id}:done!")
