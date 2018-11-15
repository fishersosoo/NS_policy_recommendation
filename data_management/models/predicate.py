# coding=utf-8

from py2neo.ogm import RelatedFrom, Property

# PredicateType=namedtuple("PredicateType",["name"])
from data_management.models import PolicyGraphObject

PredicateValue = ["&", "|", "<=", "<", ">", ">=", "==", "IS", "HAS"]


class Predicate(PolicyGraphObject):
    in_requirement = RelatedFrom("Requirement", "HAS_PREDICATE")
    predicate_value = Property("Value")

    def __init__(self, value):
        super().__init__()
        self.predicate_value = value
