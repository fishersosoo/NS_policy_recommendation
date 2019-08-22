from data_management.config import py_client

class Industry():
	@classmethod
	def import_data(cls, industries):
		for industry, keywords in industries.items():
			result = {}
			result["field"] = industry
			result["keywords"] = keywords
			py_client.ai_system["industries"].insert_one(result)

	@classmethod
	def get_data(cls):
		return list(py_client.ai_system["industries"].find({}))

if __name__ == '__main__':
	arr = \
		{'测试':['测试1','测试2','测试3'],'测试1': ['测试啊','测试啊','测试啊']}
	Industry.import_data(arr)
	print(Industry.get_data())