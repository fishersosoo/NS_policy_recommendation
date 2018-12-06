# coding=utf-8
import sys

from condition_identification.document_parsing.html_parser import HtmlParser

sys.path.append("..")

def test_html_parser():
    html_parser = HtmlParser()
    sentences = []
    with open(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\doc\html\广州南沙新区_自贸片区_促进总部经济发展扶持办法.html', 'r',
              encoding="UTF-8") as html_file:
        sentences = html_parser.parse_document(html_parser.load_file(html_file))
        #for sentence in sentences:
            #print(sentence)
    return sentences


if __name__ == "__main__":
    print(1)
    test_html_parser()
