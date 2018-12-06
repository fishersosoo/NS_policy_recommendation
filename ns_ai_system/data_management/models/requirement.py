# coding=utf-8
from py2neo import NodeMatcher, Node, RelationshipMatcher, Relationship

from data_management.models import BaseInterface, UUID, graph_
from data_management.models.predicate import Predicate


class Requirement(BaseInterface):
    @classmethod
    def create(cls, **kwargs):
        node = Node(cls.__name__, id=UUID(), **kwargs)
        graph_.create(node)
        return node["id"]

    @classmethod
    def update_by_id(cls, id_, *args, **kwargs):
        node = NodeMatcher(graph_).match(cls.__name__, id=id_).first()
        if node is None:
            raise Exception(f"{cls.__name__} not found")
        else:
            node.labels.update(args)
            node.update(kwargs)
        graph_.push(node)

    @classmethod
    def set_predicate(cls, id_, predicate_id):
        _, _, node = cls.find_by_id(id_)
        _, _, predicate_node = Predicate.find_by_id(predicate_id)
        relationship = RelationshipMatcher(graph_).match((node,), "HAS_PREDICATE").first()
        if relationship is not None:
            old_node = relationship.end_node()
            graph_.separate(relationship)
            graph_.delete(old_node)
        relationship = Relationship(node, "HAS_PREDICATE", predicate_node)
        graph_.create(relationship)

    @classmethod
    def set_object(cls, id_, object_id):
        _, _, node = cls.find_by_id(id_)
        _, _, object_node = BaseInterface.find_by_id_in_graph(object_id)
        if "Subject" not in object_node.labels:
            object_node.add_label("Subject")
        relationship = RelationshipMatcher(graph_).match((node,), "HAS_OBJECT").first()
        if relationship is not None:
            graph_.separate(relationship)
        relationship = Relationship(node, "HAS_OBJECT", object_node)
        graph_.create(relationship)

    @classmethod
    def set_subject(cls, id_, subject_id):
        _, _, node = cls.find_by_id(id_)
        _, _, subject_node = BaseInterface.find_by_id_in_graph(subject_id)
        if "Subject" not in subject_node.labels:
            subject_node.add_label("Subject")
            # graph_.push(subject_node)
        relationship = RelationshipMatcher(graph_).match((node,), "HAS_SUBJECT").first()
        if relationship is not None:
            graph_.separate(relationship)
        relationship = Relationship(node, "HAS_SUBJECT", subject_node)
        graph_.create(relationship)


if __name__ == "__main__":
    r_id = Requirement.create()
    p_id = Predicate.create(value="&")
    p_id_2 = Predicate.create(value="|")
    Requirement.set_predicate(r_id, p_id)
    Requirement.set_predicate(r_id, p_id_2)
    print(Requirement.find_by_id(r_id))
