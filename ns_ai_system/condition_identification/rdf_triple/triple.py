class Triple:
    """保存三元组
    用于保存三元组，存储内容包括(s, r, o)三元组、每个三元组对应的原文

    Attributes:
        filed: [] value可能对应的filed
        relation:str 关系“大于、小于、位于、是、否”
        value: str 值
        sentence: str 对应原文
        sentence_id: str 对应原文的id
    """

    def __init__(self):
        self.field = []
        self.relation = ''
        self.value = ''
        self.sentence = ''
        self.sentence_id = ''

    def to_dict(self):
        """
        转化为dict

        :return:
        """
        return {"fields": self.field, "relation": self.relation, "value": self.value, "sentence": self.sentence,"sentence_id":self.sentence_id}

    def __repr__(self):
        """打印三元组
        """
        return str((self.field, self.relation, self.value))