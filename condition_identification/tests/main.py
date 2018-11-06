# coding=utf-8
from condition_identification.dict_management.dict_management import EntityDict
from condition_identification.document_parsing.html_parser import HtmlParser
from condition_identification.word_segmentation.jieba_segmentation import Segmentation

if __name__=="__main__":
    # get sentences
    html_parser = HtmlParser()
    sentences = []
    with open(r'Y:\Nansha AI Services\condition_identification\res\doc\html\广州南沙新区_自贸片区_促进总部经济发展扶持办法.html', 'r',
              encoding="UTF-8") as html_file:
        sentences = html_parser.parse_document(html_parser.load_file(html_file))
    # init jieba
    segmentation = Segmentation()
    # load dict
    entity_set = EntityDict()
    entity_set.load_dict(r'Y:\Nansha AI Services\condition_identification\res\word_segmentation\norm_dict', "norm")
    entity_set.load_dict(r'Y:\Nansha AI Services\condition_identification\res\word_segmentation\category_dict',
                         "category")
    entity_set.load_dict(r'Y:\Nansha AI Services\condition_identification\res\word_segmentation\qualification_dict',
                         "qualification")
    for entity in entity_set.entity_set:
        segmentation.tokenizer.add_word(entity)
    # process a sentence
    for sentence in sentences:
        words=segmentation.cut(sentence)

