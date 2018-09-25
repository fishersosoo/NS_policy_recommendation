# coding=UTF-8
from html.parser import HTMLParser


class DocHTMLParser(HTMLParser):
    """
    处理html格式的政策文档
    """

    def __init__(self):
        super().__init__()
        self._sentence = []
        self.tag = ''

    def handle_starttag(self, tag, attrs):
        self.tag = tag
        # print(self.tag)

    def handle_data(self, data):
        # print(data)
        if self.tag == "p" or self.tag=='span' or self.tag=='br':
            self._sentence.append(data)

    @property
    def sentence(self):
        return self._sentence


class HtmlParser:
    """
    处理html格式的政策文档
    """

    def __init__(self):
        pass

    def load_file(self, file):
        """
        加载文件，返回文档字符串

        :type file: file
        :param file: 文档文件
        :return: 文档字符串
        """
        html_str = file.read()
        return html_str

    def parse_document(self, doc_str):
        """
        将输入的文档字符串切分成多个句子

        :type doc_str: str
        :param doc_str: 文档字符串
        :return: 使用tuple保存切分后的句子
        """
        parser = DocHTMLParser()
        parser.feed(doc_str)
        sentence = parser.sentence
        parser.close()
        return sentence
