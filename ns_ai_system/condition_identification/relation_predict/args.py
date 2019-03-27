import os

import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)
file_path = os.path.dirname(__file__)
####关系字典
relation_dic = {0: '小于', 1: '大于'}
#####学习率
learning_rate = 0.001
####softmax参数初始化
w = ['小于', '大于']

# gpu使用率
gpu_memory_fraction = 0.333
