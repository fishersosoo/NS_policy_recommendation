# coding=utf-8
from py2neo.ogm import RelatedTo, Property, RelatedFrom

from data_management.models import PolicyGraphObject


class Boon(PolicyGraphObject):
    __primarykey__ = "id"
    __primarylabel__ = "Boon"
    id = Property("id")
    content = Property("content")
    belong_to = RelatedFrom("Policy", "HAS_BOON")
    requirements = RelatedTo("Requirement", "NEED")
