# coding=utf-8

import os
from collections import namedtuple

from condition_identification.dict_management.properties_utiil import Properties
from data_management.models.words import Word

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
            print(path + ":" + category + "-dict is not exist")

    @property
    def entity_set(self):
        return tuple(self._entity_set)

    @property
    def entity_word(self):
        words = []
        for enti_word in self._entity_set:
            words.append(enti_word.name)
        return words


class DictManagement:
    @classmethod
    def reload_dict(cls):
        """
        从数据库中获取词典更新到本地字库中
        :return:
        """
        from distutils.sysconfig import get_python_lib
        lib_path = get_python_lib()
        property_file_path = os.path.join(lib_path, "pyhanlp", "static", "hanlp.properties")
        hanlp_properties = Properties()
        hanlp_properties.load(open(property_file_path, encoding="utf-8"))
        root_path = hanlp_properties["root"]
        custom_dictionary_path = hanlp_properties["CustomDictionaryPath"]
        if "data/dictionary/custom/category.txt; norm.txt; qualification.txt" not in custom_dictionary_path:
            custom_dictionary_path += "data/dictionary/custom/category.txt; norm.txt; qualification.txt"
            hanlp_properties["CustomDictionaryPath"] = custom_dictionary_path
            hanlp_properties.store(open(property_file_path, "w", encoding="utf-8"))
        dict_types = ["Category", "Norm", "Qualification"]
        dictionary_dir = os.path.join(root_path, "data/dictionary/custom/")
        for dict_type in dict_types:
            words = [node["word"] for node in Word.list_all(dict_type)]
            with open(os.path.join(dictionary_dir, f"{dict_type.lower()}.txt"), "w", encoding="utf-8") as file:
                file.write("\n".join(words))
        print("reloading dictionary")
        from pyhanlp import CustomDictionary
        CustomDictionary.reload()
        print("done reload dictionary")

    @classmethod
    def upload_dict(cls, directory):
        """
        读取本地字典文件，上传到数据库中
        注意:会清除数据库中已有的词典数据
        （用于初始数据库）

        :return:
        """
        Word.clear()
        dict_types = ["Category", "Norm", "Qualification"]
        for dict_type in dict_types:
            with open(os.path.join(directory, f"{dict_type.lower()}_dict"), 'r', encoding='utf-8') as dict_file:
                for word in dict_file.readlines():
                    word = word.strip("\n")
                    print(word)
                    Word.create(dict_type, word)


if __name__ == "__main__":
    # DictManagement.upload_dict("../res/word_segmentation")
    DictManagement.reload_dict()
