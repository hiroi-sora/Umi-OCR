from bottle import run, route
from PySide2.QtCore import QThreadPool, QRunnable

import os
import time
from ..platform import Platform
from ..utils import pre_configs

CurrentPort = -1


@route("/umiocr")
def _umiocr():
    v = os.environ["APP_VERSION"]
    return f"Umi-OCR v{v}"


class _WorkerClass(QRunnable):
    def run(self):
        run(host="localhost", port=CurrentPort, debug=True)


_Worker = _WorkerClass()


# 启动web服务
def runUmiWeb():
    global CurrentPort
    # 获取端口号
    port = pre_configs.getValue("server_port")  # 记录的端口号
    usedPorts = Platform.getUsedPorts()  # 已占用的端口号
    print(usedPorts)
    while port in usedPorts:  # 找到下一个未占用的
        port += 1
    if port > 65535:
        raise ValueError(f"在范围{port}~65535内找不到可用的端口号！")
    CurrentPort = port
    # 启动工作线程
    threadPool = QThreadPool.globalInstance()  # 获取全局线程池
    threadPool.start(_Worker)
    return port


# 切换端口号（下次启动生效）
def setPort(port):
    pre_configs.setValue("server_port", port)
