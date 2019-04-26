# coding=utf-8
"""
导出模型
加载已经训练好的checkpoint，导出部署模型
"""
import tensorflow as tf

from model.bert_vec.modeling import Setting, export

flags = tf.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('config_file', r"Z:\nlptest\res\chinese_L-12_H-768_A-12\bert_config.json", 'bert_config.json的路径')
flags.DEFINE_string('vocab_file', r"Z:\nlptest\res\chinese_L-12_H-768_A-12\vocab.txt", 'vocab.txt的路径')
flags.DEFINE_string('init_checkpoint', r"Z:\nlptest\res\chinese_L-12_H-768_A-12\bert_model.ckpt", '模型的ckpt路径，如"bert_model.ckpt"')
flags.DEFINE_string('output_dir', r"Z:\docker\model", '模型保存的目录')


def main():
    settting = Setting(data_dir="",
                       config_file=FLAGS.config_file,
                       vocab_file=FLAGS.vocab_file,
                       output_dir=FLAGS.output_dir,
                       init_checkpoint=FLAGS.init_checkpoint,
                       max_seq_length=32,
                       train_batch_size=16,
                       num_train_epochs=20.0,
                       tpu_name=None
                       )
    export(settting)


if __name__ == '__main__':
    # flags.mark_flag_as_required("config_file")
    # flags.mark_flag_as_required("vocab_file")
    # flags.mark_flag_as_required("init_checkpoint")
    # flags.mark_flag_as_required("output_dir")
    # tf.app.run()
    settting = Setting(data_dir=r"Z:\nlptest\res\data_1",
                       config_file=FLAGS.config_file,
                       vocab_file=FLAGS.vocab_file,
                       output_dir=FLAGS.output_dir,
                       init_checkpoint=FLAGS.init_checkpoint,
                       max_seq_length=32,
                       train_batch_size=16,
                       num_train_epochs=20.0,
                       tpu_name=None
                       )
    export(settting)