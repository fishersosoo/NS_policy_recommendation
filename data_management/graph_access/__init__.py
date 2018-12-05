# coding=utf-8
"""
提供图数据访问接口
使用duck typing，不用抽象基类
"""
import sys

from treelib import Node as TreeNode

from models.boon import Boon
from models.object_ import Object
from models.policy import Policy
from models.predicate import Predicate
from models.requirement import Requirement
from models.subject import Subject

sys.path.append("..")
try:
    from ..bonus_identify.Tree import DocTree
    from ..predicate_extraction.tuple_bonus_recognize import TupleBonus
except Exception:
    from bonus_identify.Tree import DocTree
    from predicate_extraction.tuple_bonus_recognize import TupleBonus
from predicate_extraction.tuple_bonus_recognize import Bonus_Condition_Tree


def build_policy_graph(p_id, tree):
    """

    :type tree: Bonus_Condition_Tree
    """
    print("build graph")
    root = tree.root
    for boon_node in tree.children(root):
        boon_id = DFS_bulid_graph(boon_node, tree)
        Policy.add_boons(p_id, [boon_id])

    # for boon in tree.get_all_bonus():
    #     print(boon.get_node_type(boon))


def DFS_bulid_graph(root, tree):
    """
    深度优先遍历将树结构保存到neo4j
    :type root: TreeNode
    :type tree: Bonus_Condition_Tree

    """
    print("build node",root)
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
            predicate = Predicate.create(value=root.data["CONTENT"].lower())
            Requirement.set_predicate(requirement, predicate)
            Requirement.set_object(requirement, left_child)
            Requirement.set_subject(requirement, right_child)
            sub_requirement_children.append(requirement)
        if len(sub_requirement_children) !=0:
            return sub_requirement_children.pop(0)
        else:
            requirement = Requirement.create()
            return requirement
    if root.data["TYPE"] == "CONDITION":
        print(root.data["CONTENT"])
        s,p,o = root.data["CONTENT"]
        requirement = Requirement.create()
        # TODO:这里三元组没有存储类别所以暂时没办法存储类型，下一版本predicate的链接需要单独开
        subject = Subject.create("Null", value=s)
        object_ = Object.create("Literal", value=o)
        predicate = Predicate.create(content=p)
        Requirement.set_predicate(requirement, predicate)
        Requirement.set_subject(requirement, subject)
        Requirement.set_object(requirement, object_)
        return requirement


if __name__ == "__main__":
    policy_path = r'Y:\Nansha AI Services\condition_identification\condition_identification\bonus_identify\广州南沙新区(自贸片区)促进总部经济发展扶持办法｜广州市南沙区人民政府.txt'
    import os

    policy = Policy.create(content=os.path.split(policy_path)[1])
    tree = DocTree()
    tree.construct(policy_path)
    dict_dir = r"Y:\Nansha AI Services\condition_identification\res\word_segmentation"
    tuplebonus = TupleBonus(dict_dir, if_edit_hanlpdict=0)
    tuplebonus.bonus_tuple_analysis(tree)
    build_policy_graph(policy, tuplebonus.get_bonus_tree())
