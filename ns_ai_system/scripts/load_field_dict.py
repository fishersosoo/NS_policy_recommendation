# coding=utf-8

from data_management.models.word import Word

if __name__ == '__main__':
    Word.load_from_file(r"Y:\Nansha AI Services\condition_identification\ns_ai_system\res\field_dict.csv")
