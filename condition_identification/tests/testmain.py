# coding=utf-8
import sys
import re
sys.path.append("..")
from dict_management.dict_management import EntityDict
from document_parsing.html_parser import HtmlParser
from word_segmentation.jieba_segmentation import Segmentation
from entity_link.entity_recognizer import EntityRecognizer
from syntax_analysis.sentence_analysis import HanlpSynataxAnalysis
from predicate_extraction.tuple_extracter import TupleExtracter
import jieba.posseg as pseg

if __name__=="__main__":
    # get sentences
    html_parser = HtmlParser()
    sentences = []
    with open(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\doc\html\广州南沙新区_自贸片区_促进总部经济发展扶持办法.html', 'r',
              encoding="UTF-8") as html_file:
        sentences = html_parser.parse_document(html_parser.load_file(html_file))
        #print(sentences)

    # init jieba
    segmentation = Segmentation()

    # load dict
    entity_set = EntityDict()
    entity_set.load_dict(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\norm_dict', "norm")
    entity_set.load_dict(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\category_dict',"category")
    entity_set.load_dict(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\qualification_dict',"qualification")
    #print(entity_set.entity_set)

    for entity in entity_set.entity_word:
        segmentation.tokenizer.add_word(entity,1000)
        #print(entity)

    # process a sentence
    cut_sentences=[]
    for sentence in sentences:
        #wordss=segmentation.cut(sentence)
        words = segmentation.psegcut(sentence)
        cut_sentences.append(tuple(words))

    # recognize entity
    sentence_entity_dict = {}
    entityrecognizer = EntityRecognizer()
    for i,sentence in enumerate(cut_sentences):
        result = entityrecognizer.entity_mark(sentence,entity_set.entity_set)
        if len(result) > 0:
            sentence_entity_dict[i] = result
    #print(sentence_entity_dict)

    # analyse sentence and extract three-tuples
    hanlpanalysis = HanlpSynataxAnalysis()
    extracter = TupleExtracter()
    sentence_tuple = []
    sentence_spo_dict= {}

    for key in sentence_entity_dict:
        sentence_entity = sentence_entity_dict[key]

        sentence = sentences[key]
        #sentence = hanlpanalysis.sentencePreprocessing(sentence,sentence_entity)

        sentences[key] = sentence
        split_sentence = re.split("[;；。,，]",sentence)
        spoarray=[]

        for one_sentence in split_sentence:
            if len(one_sentence) == 0:
                continue

            syntaxtuple = hanlpanalysis.parseDependency(one_sentence)
            spo_tuple = extracter.predicate_extraction(syntaxtuple,sentence_entity)
            if spo_tuple != None:
                spoarray.append(spo_tuple)
        if len(spoarray) > 0:
            sentence_spo_dict[key] = spoarray

    for key in sentence_spo_dict:
        print(sentences[key])
        print(sentence_spo_dict[key])
        print("\n")

