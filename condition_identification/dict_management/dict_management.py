# coding=utf-8
from collections import namedtuple

entity = namedtuple('entity', ['name', 'category'])


class EntityDict:
    def __init__(self):
        self._entity_set = []

    def load_dict(self, path, category):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                word = f.readline()
                while word != "":
                    self._entity_set.append(entity(name=word.strip('\n'), category=category))
                    word = f.readline()
        except FileNotFoundError:
            print(path+":"+category+"-dict is not exist")

    @property
    def entity_set(self):
        return tuple(self._entity_set)

    @property
    def entity_word(self):
        words = []
        for enti_word in self._entity_set:
            words.append(enti_word.name)
        return words


if __name__ == "__main__":
    entity_set = EntityDict()
    entity_set.load_dict(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\norm_dict', "norm")
    entity_set.load_dict(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\category_dict',
                         "category")
    entity_set.load_dict(r'C:\Users\edward\Documents\GitHub\NS_policy_recommendation\res\word_segmentation\qualification_dict',
                         "qualification")
    print(entity_set.entity_set)
