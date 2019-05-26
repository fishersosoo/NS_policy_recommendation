# coding=utf-8
import os
import subprocess
import tempfile


def get_text_from_doc_bytes(input, remove_file=True):
    """
    读取doc文件的二进制，返回文件中的文本
    将doc文本的字节存放到临时文件中，利用系统uno命令调用libreoffice将文件转为txt，将txt的文字返回
    :param remove_file: 是否删除转换前的文件
    :param input:
    :return: doc文件中的文本
    """
    if isinstance(input, bytes):
        doc_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".doc")
        doc_temp_file.write(input)
        doc_temp_file.close()
    else:
        doc_temp_file = input
    subprocess.call(["unoconv", "-f", "txt", doc_temp_file.name])
    txt_temp_file_path = os.path.splitext(doc_temp_file.name)[0] + ".txt"
    with open(txt_temp_file_path, encoding="utf-8") as txt_temp_file:
        text = txt_temp_file.read()
    if remove_file:
        os.remove(doc_temp_file.name)
    os.remove(txt_temp_file_path)
    if text == "" or text is None:
        raise Exception("无法读取doc内容")
    return text
