# coding=utf-8
from py2neo.ogm import Property, Label, RelatedFrom

from data_management.models import PolicyGraphObject


class Subject(PolicyGraphObject):
    __primarylabel__ = "Subject"
    norm = Label("Norm")

    value = Property("value")

    in_requirement = RelatedFrom("Requirement", "HAS_SUBJECT")
    in_sub_requirement = RelatedFrom("SubRequirement", "HAS_SUBJECT")

    def __init__(self, label="Norm", value=None):
        super().__init__()
        self.__setattr__(label, True)
        if value is not None:
            self.value = value
