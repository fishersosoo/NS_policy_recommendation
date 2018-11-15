# coding=utf-8
from py2neo.ogm import RelatedTo, Property

from data_management.models import PolicyGraphObject
from data_management.models.boon import Boon


class Policy(PolicyGraphObject):
    __primarykey__ = "id"
    __primarylabel__ = "Policy"
    id = Property("id")

    boons = RelatedTo(Boon, "HAS_Boon")
    content = Property("content")
