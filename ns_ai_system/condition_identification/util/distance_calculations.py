# coding=utf-8
import numpy as np
from condition_identification.args import cos_similarity_bias
from condition_identification.args import cos_similarity_multiplier


def cos_sim(vector_a, vector_b):
    """计算两个词向量之间的相似度

    将bert词向量转化为矩阵然后计算他们的相似度

    Args:
        vector_a: 向量 a ,list 或者 numpy数组
        vector_b: 向量 b，list 或者 numpy数组
    Returns:
          sim: float,两个向量之间的相似度

    """
    # 计算两个向量的相似度
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    de_nom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / de_nom
    sim = cos_similarity_bias + cos_similarity_multiplier * cos
    return sim


