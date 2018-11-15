# coding=utf-8
from py2neo.ogm import RelatedTo, RelatedFrom

from data_management.models import PolicyGraphObject
from data_management.models.boon import Boon
from data_management.models.object_ import Object
from data_management.models.predicate import Predicate
from data_management.models.subject import Subject


class SubRequirement(PolicyGraphObject):
    in_requirement = RelatedFrom("Requirement", "HAS_SUBREQUIREMENT")
    in_sub_requirement = RelatedFrom("SubRequirement", "HAS_SUBREQUIREMENT")
    sub_requirements = RelatedTo("SubRequirement", "HAS_SUBREQUIREMENT")
    subject = RelatedTo(Subject, "HAS_SUBJECT")
    object_ = RelatedTo(Object, "HAS_OBJECT")
    predicate = RelatedTo(Predicate, "HAS_PREDICATE")

    def set_subject(self, subject_node):
        self.subject.add(subject_node)

    def set_object_(self, object_node):
        self.object_.add(object_node)


class Requirement(PolicyGraphObject):
    predicate = RelatedTo(Predicate, "HAS_PREDICATE")
    sub_requirements = RelatedTo(SubRequirement, "HAS_SUBREQUIREMENT")
    support = RelatedFrom(Boon, "NEED")
    subject = RelatedTo(Subject, "HAS_SUBJECT")
    object_ = RelatedTo(Object, "HAS_OBJECT")
