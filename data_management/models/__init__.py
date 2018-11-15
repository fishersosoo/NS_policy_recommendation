from uuid import uuid1

from py2neo.ogm import GraphObject, Property


class PolicyGraphObject(GraphObject):
    __primarykey__ = "id"

    id = Property("id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = str(uuid1())
