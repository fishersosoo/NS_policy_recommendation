# coding=utf-8
from py2neo import Node, NodeMatcher

from data_management.models import BaseInterface, UUID, graph_


class Boon(BaseInterface):
    @classmethod
    def create(cls, **kwargs):
        # kwargs["id"]=
        node = Node(cls.__name__, id=UUID(), **kwargs)
        graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, **kwargs):
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        else:
            node.update(kwargs)
        graph_.push(node)


if __name__ == "__main__":
    id = Boon.create(content="""四、实施高学历人才补贴
对新引进落户工作的全日制本科及以上学历、学士及以上学位人才发放住房补贴，其中本科生2万元，硕士研究生4万元，博士研究生6万元。""")
    print(Boon.find_by_id(id))
    Boon.update_by_id(id, content="""对新设立的院士工作站，给予最高100万元的开办经费资助;""")
    print(Boon.find_by_id(id))
    Boon.remove_by_id(id)
    print(Boon.find_by_id(id))
