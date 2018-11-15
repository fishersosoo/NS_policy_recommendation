# coding=utf-8
from py2neo.ogm import Property, Label, RelatedFrom

from data_management.models import PolicyGraphObject


class Object(PolicyGraphObject):
    category = Label("Category")
    qualification = Label("Qualification")
    literal = Label("Literal")

    value = Property("value")

    in_requirement = RelatedFrom("Requirement", "HAS_OBJECT")
    in_sub_requirement = RelatedFrom("SubRequirement", "HAS_OBJECT")

    def __init__(self, label, value=None):
        super().__init__()
        self.__setattr__(label, True)
        if value is not None:
            self.value = value
