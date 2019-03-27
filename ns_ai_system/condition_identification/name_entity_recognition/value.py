import re
from collections import defaultdict

from pyhanlp import *

from condition_identification.name_entity_recognition.args import *
from condition_identification.name_entity_recognition.util import cos_sim


def _get_values_from_files(value_file_dir):
    """
    从指定目录的文件中加载各个字段处理后的value集合

    :param value_file_dir: value文件目录
    :return: {字段名:set(value)}
    """
    values = defaultdict(set)
    for file in os.listdir(value_file_dir):
        value_set = set()
        with open(os.path.join(value_file_dir, file), encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if line != '':
                    value_set.add(line)
            values[file] = value_set
    return values


class Value(object):
    def __init__(self, value_file_dir):
        self.field_values_map = _get_values_from_files(value_file_dir)
        self.value_dict = defaultdict(list)

    def compare_similarity(self, line, value, bc):
        max_value = 0
        max_word = ''
        for word in value:
            word = word.strip()
            flag = False
            for term in HanLP.segment(word):
                if term.word in line:
                    flag = True
                    break
            if flag:
                value = cos_sim(bc.encode([line]), bc.encode([word]))
                if max_value < value:
                    max_value = value
                    max_word = word
        return max_value, max_word

    def construct_value_dict(self, regs, bc):
        for line in regs:
            if self.idf_nums(line):
                self.value_dict[line] = NUMS
            elif self.idf_address(line):
                self.value_dict[line] = ADDRESS
            else:
                candidate_value = []
                for field in self.field_values_map:
                    values = self.field_values_map[field]
                    max_value, max_word = self.compare_similarity(line, values, bc)
                    if max_word != '' and max_value > 0.945:
                        candidate_value.append(field)

                if candidate_value:
                    self.value_dict[line] = candidate_value
        return self.value_dict

    def get_fileddict(self):
        return self.value_dict

    # TODO 还有中文的数字一二三四没有拆
    # TODO 这里应该放再抽关键字之前，因为有可能关键字没抽到
    def idf_nums(self, word):
        p = r"\d*.*"
        pattern = re.compile(p)
        match = pattern.findall(word)[0]
        if match != '' and '元' in word:
            return True
        else:
            return False

    # 数据库字段的地址就用地的相似度去找，
    def idf_address(self, sentence):
        segment = HanLP.newSegment().enablePlaceRecognize(False)
        term_list = segment.seg(sentence)
        natures = [str(i.nature) for i in term_list]
        if 'ns' in natures:
            return True
        else:
            return False
