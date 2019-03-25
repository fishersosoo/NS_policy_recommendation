# -*- coding: UTF-8 -*-
# !/usr/bin/python
# 从网上download到minist相关的数据以及处理函数

import tensorflow as tf
from bert_serving.client import BertClient
import pandas as pd
import numpy as np
import os
from relation_predict import args
relation_dic=args.relation_dic
# a classifier with only softmax layer
from sklearn.model_selection import train_test_split
def get_examples():
    df=pd.read_csv(args.file_path+'data/train.csv')
    df=df[df['relation']!=0].reset_index(drop=True)
    bc=BertClient()
    train=bc.encode(df['sentence'].values.tolist())
    label=pd.get_dummies(df['relation'])
    labels=np.array(label.values)
    x_train,x_test,y_train,y_test=train_test_split(train,labels,test_size=0.25)
    return x_train,x_test,y_train,y_test

def train_model():
    bc=BertClient()
    # x是一个N * 784的矩阵，784指的是28 * 28 的图片拉伸为一行
    # N为批数，由用户在运行时指定。
    # x存放的是每一批的训练数据，是不断变更的，因此需要用到tf中的feed方法，因此在这里只用占位符
    # None指的是这个维度的值是任意的，在这里是输入的batch的大小是任意的
    www=bc.encode(args.w).T
    init = tf.constant_initializer(www)
    W=tf.get_variable(name='w', shape=[768,2], initializer=init)

    x = tf.placeholder(tf.float32, [None, 768],name="x")

    # 用于存放真实标签
    y_ = tf.placeholder("float", [None,2])

    # variable是tensorflow中可以被修改的变量

    # W = tf.Variable(tf.zeros([768, 2]))
    b = tf.Variable(tf.zeros([2]),name='bias')

    # 一行代码实现softmax的前向传播，y是预测输出
    y = tf.nn.softmax(tf.matmul(x, W) + b)

    # 训练模型，这里用的是交叉熵，交叉熵被认为是比较好的loss function
    # reduce_sum是求张量所有元素总和的求和函数。log(y)和*（这里是点乘）都是逐个元素进行的
    # 从这里也可以看出tensorflow中的loss function 是需要自己定义的
    cross_entropy = -tf.reduce_sum(y_ * tf.log(y))

    # 用梯度下降法优化交叉熵
    # 其他优化算法也是一行代码，详情查阅文档，0.001指的是学习率
    train_step = tf.train.GradientDescentOptimizer(args.learning_rate).minimize(cross_entropy)

    # 启动session，初始化变量，这里的图用的是默认图
    init = tf.initialize_all_variables()
    saver = tf.train.Saver()

    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=args.gpu_memory_fraction)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
    sess.run(init)
    x_train,x_test,y_train,y_test=get_examples()

    # 训练模型
    for i in range(10000):
        batch_xs, batch_ys =x_train,y_train
        sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
        if i % 50 == 0:
            correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
            print( "Setp: ", i, "Accuracy: ", sess.run(accuracy, feed_dict={x: x_train, y_:y_train}))
    # 测试并输出准确率
    # tf.argmax 能给出某个tensor对象在某一维上的其数据最大值所在的索引值。由于标签向量是由0,1组成，因此最大值#1所在的索引位置就是类别标签，比如tf.argmax(y,1)返回的是模型对于任一输入x预测到的标签值，
    # 而 tf.argmax(y_,1) 代表正确的标签，我们可以用 tf.equal 来检测我们的预测是否真实标签匹配(索引位置一样表#示匹配)。
    # y的维度可选值是[0, 1]
    saver.save(sess, args.file_path+"./model/model.ckpt")
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))

    # 上行代码会给我们一组布尔值。为了确定正确预测项的比例，我们可以把布尔值转换成浮点数，然后取平均值。例如，#[True, False, True, True] 会变成 [1,0,1,1] ，取平均值（reduce_mean）后得到 0.75.
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

    # 将预测集输入并输出准确率
    print (sess.run(accuracy, feed_dict={x: x_test, y_: y_test}))

    # 总结：placeholder用于存放外部输入的tensor，variable用于存放内部自己变化的tensor
def predict_relation(value):
    predict_label=[]
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
    module_path = os.path.dirname(__file__)
    print(module_path)
    saver = tf.train.import_meta_graph(module_path+'/model/model.ckpt.meta')
    saver.restore(sess, tf.train.latest_checkpoint(module_path+'/model'))
    graph = tf.get_default_graph()
    W = graph.get_tensor_by_name("w:0")
    x = graph.get_tensor_by_name("x:0")
    b=graph.get_tensor_by_name("bias:0")
    feed_dic={x:value}
    y = tf.nn.softmax(tf.matmul(x, W) + b)
    predict_value=sess.run(y,feed_dic)
    # print(predict_value)
    labels=sess.run(tf.argmax(predict_value,1))
    return relation_dic[labels[0]]
if __name__ == '__main__':
    bc=BertClient()
    v=bc.encode(['高于500万元'])
    print(predict_relation(v))
    # train_model()
    # print(args.file_path)