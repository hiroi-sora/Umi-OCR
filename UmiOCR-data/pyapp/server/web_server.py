# =========================================================
# =======                 Web服务器                 ========
# ======= http接口可复用于跨进程命令行、防止多开等方面 ========
# =========================================================

from bottle import Bottle, ServerAdapter
from PySide2.QtCore import QThreadPool, QRunnable
from wsgiref.simple_server import make_server, WSGIServer

import os
from ..platform import Platform
from ..utils import pre_configs

UmiWeb = Bottle()


# ============================== 路由 ==============================


@UmiWeb.route("/")
@UmiWeb.route("/umiocr")
def _umiocr():
    v = os.environ["APP_VERSION"]
    print("1111111111")
    return f"Umi-OCR v{v}"


@UmiWeb.route("/test")
def _test():
    return f"test!!!!!!!!!!!"


# =============== 自定义服务器适配器，方便控制服务终止 ==============================
class _WSGIRefServer(ServerAdapter):
    # https://stackoverflow.com/questions/11282218/bottle-web-framework-how-to-stop

    class CustomWSGIServer(WSGIServer):  # 定制服务器
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.activeConnections = set()  # 当前活跃连接

        def process_request(self, request, client_address):
            # 记录活跃的连接
            self.activeConnections.add(request)
            super().process_request(request, client_address)

        def close_all_request(self):  # 关闭所有活跃的连接
            import socket

            for request in self.activeConnections:
                try:
                    request.shutdown(socket.SHUT_RDWR)
                    request.close()
                    print("强制关闭连接", request)
                except OSError:
                    pass
                except Exception as e:
                    print("[Error] 强制关闭连接异常：", e)

    def run(self, handler):
        import atexit  # 退出处理

        atexit.register(self.stop)  # 注册程序终止时停止线程
        self.server = make_server(
            self.host,
            self.port,
            handler,
            server_class=self.CustomWSGIServer,
            **self.options,
        )
        self.server.serve_forever()

    def stop(self):  # 服务终止
        # self.server.server_close() # 备选方案，但会导致 bad fd 异常
        print("###  WEB服务器准备关闭！")
        self.server.close_all_request()  # 强制关闭客户端连接
        self.server.shutdown()  # 关闭服务器
        print("###  WEB服务器已关闭！")


# ============================== 线程类 ==============================

CurrentPort = -1  # 记录当前端口号


class _WorkerClass(QRunnable):
    def run(self):
        self._server = _WSGIRefServer(port=CurrentPort)
        UmiWeb.run(server=self._server)


_Worker = _WorkerClass()


# ============================== 控制接口 ==============================


# 搜索可用端口号
def getFreePort(start):
    usedPorts = Platform.getUsedPorts()  # 获取已占用的端口号
    for i in range(start, 65536):
        if i not in usedPorts:
            return i
    for i in range(1024, start):
        if i not in usedPorts:
            return i
    return -1


# 启动web服务
def runUmiWeb():
    global CurrentPort
    CurrentPort = port = pre_configs.getValue("server_port")  # 记录的端口号
    port = getFreePort(port)  # 搜索可用端口号
    if port > 0:  # 有可用端口，启动工作线程
        if CurrentPort != port:  # 端口有变更，则记录变更
            CurrentPort = port
            setPort(port)
        threadPool = QThreadPool.globalInstance()  # 获取全局线程池
        threadPool.start(_Worker)
    return port


# 切换端口号（下次启动生效）
def setPort(port):
    pre_configs.setValue("server_port", port)
