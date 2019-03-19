# coding=utf-8
class ParagraphExtractOutput:
    """
    用于保存paragraph_extract函数的结果

    """

    def __init__(self):
        raise NotImplementedError("Not Implemented")


def paragraph_extract(text):
    """
    根据指南的标题结构，抽取不同部分信息

    :type text: str
    :param text: 指南文本
    :return 返回ParagraphExtractOutput， 如果指南格式不符合要求则返回None


    """
    raise NotImplementedError("Not Implemented")


class Triples:
    """
    用于保存多个条件三元组，存储内容包括了多个(s, r, o)三元组、每个三元组对应的原文、三元组之间的and和or关系

    """

    def __init__(self):
        raise NotImplementedError("Not Implemented")

    def __repr__(self):
        """
        打印结果

        :return:
        """
        raise NotImplementedError("Not Implemented")


def triple_extract(paragraph_extract_output):
    """
    提取条件三元组

    :type paragraph_extract_output: ParagraphExtractOutput
    :param paragraph_extract_output: paragraph_extract()的返回
    :return: 返回Triples
    """
    raise NotImplementedError("Not Implemented")


if __name__ == '__main__':
    file_path = r""
    text = ""
    try:
        with open(file_path) as f:
            text = f.read()
    except:
        pass
    paragraph_extrac_output = paragraph_extract(text)
    triples = triple_extract(paragraph_extrac_output)
    print(triples)
