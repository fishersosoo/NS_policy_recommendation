from data_management.config import py_client
from data_management.models import BaseInterface

class Relation(BaseInterface):
    @classmethod
    def list_relation(cls):
        """

        Returns:
        返回所有指南记录列表

        """
        return list(py_client.ai_system["relations"].find({}))

if __name__=='__main__':
    print(Relation.list_relation())