# coding=utf-8
from collections import namedtuple

entity = namedtuple('entity', ['name', 'category'])


class EntityDict:
    def __init__(self):
        self._entity_set = []

    def load_dict(self, path, category):
        with open(path, 'r', encoding='utf-8') as f:
            word = f.readline()
            while word != "":
                self._entity_set.append(entity(name=word.strip('\n'), category=category))
                word = f.readline()

    @property
    def entity_set(self):
        return tuple(self._entity_set)


if __name__ == "__main__":
    entity_set = EntityDict()
    entity_set.load_dict(r'Y:\Nansha AI Services\condition_identification\res\word_segmentation\norm_dict', "norm")
    entity_set.load_dict(r'Y:\Nansha AI Services\condition_identification\res\word_segmentation\category_dict',
                         "category")
    entity_set.load_dict(r'Y:\Nansha AI Services\condition_identification\res\word_segmentation\qualification_dict',
                         "qualification")
    print(entity_set._entity_set)
