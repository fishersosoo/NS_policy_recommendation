# coding=utf-8
import numpy as np


def cos_sim(vector_a, vector_b):
    """计算两个向量之间的相似度

    将向量转化为矩阵然后计算他们的相似度

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
    sim = 0.5 + 0.5 * cos
    return sim


