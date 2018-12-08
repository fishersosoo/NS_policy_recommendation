# coding=utf-8
from condition_identification.predicate_extraction.tupletree_api import construct_tupletree_by_str
from data_management.models.boon import Boon
from data_management.models.object_ import Object
from data_management.models.policy import Policy
from data_management.models.predicate import Predicate
from data_management.models.requirement import Requirement
from data_management.models.subject import Subject


def build_policy_graph(text, policy_id, policy_name):
    """

    :param text:
    :param policy_id:
    :param policy_name:
    :return:
    """
    policy = Policy.create(policy_id=policy_id, policy_name=policy_name)
    tree = construct_tupletree_by_str(text)
    root = tree.root
    for boon_node in tree.children(root):
        boon_id = DFS_bulid_graph(boon_node, tree)
        Policy.add_boons(policy, [boon_id])

    # for boon in tree.get_all_bonus():
    #     print(boon.get_node_type(boon))


def DFS_bulid_graph(root, tree):
    """
    深度优先遍历将树结构保存到neo4j
    :type root: TreeNode
    :type tree: Bonus_Condition_Tree

    """
    print("build node", root)
    if root.data["TYPE"] == "BONUS":
        boon_id = Boon.create(content=root.data["CONTENT"])
        for child in tree.children(root.identifier):
            requirement_id = DFS_bulid_graph(child, tree)
            Boon.add_requirement(boon_id, requirement_id)
        return boon_id
    if root.data["TYPE"] == "LOGIC":
        # 用队列将多叉树转化为二叉树结构
        sub_requirement_children = []
        for sub_requirement_child in tree.children(root.identifier):
            sub_requirement_children.append(DFS_bulid_graph(sub_requirement_child, tree))
        while len(sub_requirement_children) >= 2:
            left_child = sub_requirement_children.pop(0)
            right_child = sub_requirement_children.pop(0)
            requirement = Requirement.create()
            predicate = Predicate.create(content=root.data["CONTENT"].lower())
            Requirement.set_predicate(requirement, predicate)
            Requirement.set_object(requirement, left_child)
            Requirement.set_subject(requirement, right_child)
            sub_requirement_children.append(requirement)
        if len(sub_requirement_children) != 0:
            return sub_requirement_children.pop(0)
        else:
            requirement = Requirement.create()
            return requirement
    if root.data["TYPE"] == "CONDITION":
        print(root.data["CONTENT"])
        s, p, o = root.data["CONTENT"].split(",")
        requirement = Requirement.create()
        # TODO:这里三元组没有存储类别所以暂时没办法存储类型，下一版本predicate的链接需要单独开
        subject = Subject.create("Null", value=s)
        object_ = Object.create("Literal", value=o)
        predicate = Predicate.create(content=p)
        Requirement.set_predicate(requirement, predicate)
        Requirement.set_subject(requirement, subject)
        Requirement.set_object(requirement, object_)
        return requirement
