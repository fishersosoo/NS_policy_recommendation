# coding=utf-8
"""
主要实现从单一的*.ini文件中读取配置，生成对应的配置dict
"""
from configparser import ConfigParser
from os import path


def get_config_dict(config_name="config.ini"):
    config_dict = dict()
    config_path = path.join(path.split(__file__)[0], config_name)
    config = ConfigParser()
    config.read(config_path)
    for section in config.sections():
        config_dict[section] = dict(config.items(section))
    return config_dict


class ConfigLoader:
    _config = get_config_dict()

    def __init__(self):
        pass

    def get(self, section, key):
        return self._config[section][key]


if __name__ == '__main__':
    print(get_config_dict())
