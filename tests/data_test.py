# coding=utf-8
from urllib import parse

if __name__ == '__main__':
    ip = "121.52.214.35"
    json_str = """{
	"uid":"43733da4883d40678dce02d80e13316a",
	"service":"getEntByKeyword",
	"params":{
		"keyword":"91110228306423540J",
		"type":1
	}
}"""
    url_param = parse.urlencode(json_str)
