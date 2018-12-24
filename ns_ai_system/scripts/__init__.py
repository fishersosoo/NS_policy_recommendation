# coding=utf-8
import os
from multiprocessing import Process

import jpype


def run():
    jvmPath = jpype.getDefaultJVMPath()
    jpype.startJVM(jvmPath)
    jpype.java.lang.System.out.println("hello world! %s" %(os.getpid()))
    jpype.shutdownJVM()


if __name__ == '__main__':
    jvmPath = jpype.getDefaultJVMPath()
    jpype.startJVM(jvmPath)
    jpype.java.lang.System.out.println("hello world! %s"%(os.getpid()))
    p = Process(target=run)
    print('Child process will start.')
    p.start()
    p.join()
    print('Child process end.')
    jpype.shutdownJVM()
