# coding=utf-8
import pandas as pd
from py2neo import Node, NodeMatcher, Relationship, RelationshipMatcher

from data_management.models import UUID, graph_, BaseInterface


class Word(BaseInterface):
    """
    词典一个词
    """

    @classmethod
    def create(cls, type_, name, field=None, **kwargs):
        """
        往数据库中添加一个字段信息，现在允许重复
        :param type_: Field 或者 Alia
        :param field: 字段名
        :param name: 字段中文
        :param kwargs:
        :return:
        """
        if type_ == "Field":
            node = Node(cls.__name__, type_, id=UUID(), name=name, field=field, **kwargs)
        else:  # Alia
            node = Node(cls.__name__, type_, id=UUID(), name=name, **kwargs)
        graph_().create(node)
        return node["id"], node

    @classmethod
    def set_alia(cls, id_, alia):
        """
        给字段设置别名，如果遇到重复的忽略
        :param id_:
        :param alia: 别名
        :return:
        """
        _, _, node = cls.find_by_id(id_)
        if NodeMatcher(graph_()).match("Alia", cls.__name__, name=alia).first() is None:
            _, alia_node = cls.create("Alia", alia)
            relationship = Relationship(node, "HAS_ALIA", alia_node)
            graph_().create(relationship)

    @classmethod
    def list_all(cls, *args):
        """
        返回所有指定类型的词典项
        :return:
        """
        return [match for match in NodeMatcher(graph_()).match(cls.__name__, *args)]

    @classmethod
    def _get_matching_score(cls, entity_name, field_name):
        if entity_name == field_name:
            return 1.
        else:
            return 0.

    @classmethod
    def get_field(cls, entity_name):
        """
        图中根据实体名称查找字段信息

        :param entity_name: 实体名称
        :return: {"name": field_node["name"], "field": field_node["field"]}，如果找不到返回None
        """
        scores = []
        for node in NodeMatcher(graph_()).match(cls.__name__):
            # 遍历计算匹配度
            scores.append([node, cls._get_matching_score(entity_name, node["name"])])
        scores.sort(key=lambda x: x[1], reverse=True)
        top_node, top_score = scores[0]
        if top_score <= 0.5:
            # 找不的匹配节点
            return None
        else:
            if "Alia" in top_node.labels:
                # TODO:这里可以对关系进行调用，这个别名的连接用了多少次
                relationship = RelationshipMatcher(graph_()).match(nodes=[None, top_node], r_type="HAS_ALIA").first()
                field_node = relationship.start_node
            else:
                field_node = top_node
            return {"name": field_node["name"], "field": field_node["field"]}

    @classmethod
    def load_from_file(cls, path, encoding="GBK"):
        """
        从csv文件
        :param path:
        :return:
        """
        df = pd.DataFrame.from_csv(path, index_col=None, encoding=encoding)
        # name	field	alias
        for index, row in df.iterrows():
            id_ = cls.create("Field", row["name"], field=row["field"])
            for alia in eval(row["alias"]):
                cls.set_alia(id_=id_, alia=alia)


if __name__ == '__main__':
    Word.clear()
