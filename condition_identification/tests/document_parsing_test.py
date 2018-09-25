# coding=utf-8
from condition_identification.document_parsing.html_parser import HtmlParser


def test_html_parser():
    html_parser = HtmlParser()
    sentences = []
    with open(r'Y:\Nansha AI Services\condition_identification\res\doc\html\广州南沙新区_自贸片区_促进总部经济发展扶持办法.html', 'r',
              encoding="UTF-8") as html_file:
        sentences = html_parser.parse_document(html_parser.load_file(html_file))
    for sentence in sentences:
        print(sentence)


if __name__ == "__main__":
    print(1)
    test_html_parser()
