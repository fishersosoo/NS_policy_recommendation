# coding=utf-8
import json
import os
import sys

from jpype import getDefaultJVMPath, startJVM, isThreadAttachedToJVM, attachThreadToJVM, JClass

from data_server.server import ns_data_access_jar_path

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
if sys.version_info[0] < 3:
    # noinspection PyUnresolvedReferences,PyCompatibility
    reload(sys), sys.setdefaultencoding("utf-8")


def _start_jvm_for_data_access():
    global STATIC_ROOT, DATA_installed_data_version, DATA_JAR_PATH, PATH_CONFIG, DATA_JAR_VERSION, DATA_DATA_PATH
    # Get ENV
    ENVIRON = os.environ.copy()

    if "DATA_JVM_XMS" in ENVIRON:
        DATA_JVM_XMS = ENVIRON["DATA_JVM_XMS"]
    else:
        DATA_JVM_XMS = "1g"
    if "DATA_JVM_XMX" in ENVIRON:
        DATA_JVM_XMX = ENVIRON["DATA_JVM_XMX"]
    else:
        DATA_JVM_XMX = "2g"
    JAVA_JAR_CLASSPATH = "-Djava.class.path=%s" % (
        ns_data_access_jar_path)
    # 启动JVM
    startJVM(
        getDefaultJVMPath(),
        JAVA_JAR_CLASSPATH,
        "-Xms%s" %
        DATA_JVM_XMS,
        "-Xmx%s" %
        DATA_JVM_XMX)


def _attach_jvm_to_thread():
    """
    use attachThreadToJVM to fix multi-thread issues: https://github.com/hankcs/pyhanlp/issues/7
    """
    if not isThreadAttachedToJVM():
        attachThreadToJVM()


class SafeJClass(object):
    def __init__(self, proxy):
        """
        JClass的线程安全版
        :param proxy: Java类的完整路径，或者一个Java对象
        """
        self._proxy = JClass(proxy) if type(proxy) is str else proxy

    def __getattr__(self, attr):
        _attach_jvm_to_thread()
        return getattr(self._proxy, attr)

    def __call__(self, *args):
        if args:
            proxy = self._proxy(*args)
        else:
            proxy = self._proxy()
        return SafeJClass(proxy)


class LazyLoadingJClass(object):
    def __init__(self, proxy):
        """
        惰性加载Class。仅在实际发生调用时才触发加载，适用于包含资源文件的静态class
        :param proxy:
        """
        self._proxy = proxy

    def __getattr__(self, attr):
        _attach_jvm_to_thread()
        self._lazy_load_jclass()
        return getattr(self._proxy, attr)

    def _lazy_load_jclass(self):
        if type(self._proxy) is str:
            self._proxy = JClass(self._proxy)

    def __call__(self, *args):
        self._lazy_load_jclass()
        if args:
            proxy = self._proxy(*args)
        else:
            proxy = self._proxy()
        return SafeJClass(proxy)


class DataServiceJavaProxy:
    _instance = None
    _DataServiceClass = LazyLoadingJClass('com.iais.DataService')

    @classmethod
    def init(cls,uid,host):
        cls._instance=DataServiceJavaProxy._DataServiceClass(uid, host)

    @classmethod
    def sendRequest(cls, service_name, params):
        """
        请求数据

        :param service_name: 数据服务名字
        :param params: 查询参数
        :return: 返回数据
        """
        return json.loads(cls._instance.sendRequest(service_name, json.dumps(params)))
