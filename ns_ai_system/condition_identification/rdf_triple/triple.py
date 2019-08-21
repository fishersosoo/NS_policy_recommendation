class Clause:
    """
    表示一个子句，一个子句有三元组对应。相当于原来的triple数据结构
    """

    def __init__(self, text=None, fields=None, relation=None, value=None):
        """
        Args:
            text: 原文
            fields: 可能的字段列表
            relation: 关系
            value: 值
        """
        if fields is None:
            fields = list()
        self.fields = fields
        self.text = text
        self.relation = None
        self.value = None

    def to_dict(self):
        return dict(fields=self.fields, text=self.text, relation=self.relation, value=self.value)

    def __repr__(self):
        """打印三元组
        """
        return str((self.fields, self.relation, self.value,self.text))


class OriginSentenceByPolicyLine:
    """
    表示原文中一个完整的条件。一个条件可能会包含有多个（逗号分割）子句
    """

    def __init__(self, text=None, clauses=None):
        """

        :param text: 原文
        :param clauses:
        """
        self.text = text
        self.type = []
        if clauses is None:
            self.clauses = list()

    def to_dict(self):
        return dict(text=self.text,type=self.type, clauses=[one.to_dict() for one in self.clauses])
