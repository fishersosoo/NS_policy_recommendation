# coding=utf-8
from pyhanlp import *
from multiprocessing import Process
import os
def func():
    print("a")
    with open("1.txt","w") as f:
        for t in HanLP.segment('你好，欢迎在Python中调用HanLP的API'):
            f.write(t.word+"|")

# func()
if __name__ == '__main__':
    print(f"main:{os.getpid()}")
    p = Process(target=func)
    p.start()
    p.join()