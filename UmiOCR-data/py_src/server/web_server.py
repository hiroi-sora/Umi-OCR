# =========================================================
# =======                 Web服务器                 ========
# ======= http接口可复用于跨进程命令行、防止多开等方面 ========
# =========================================================

from PySide2.QtCore import QThreadPool, QRunnable
from wsgiref.simple_server import make_server, WSGIServer

import os
from ..platform import Platform
from ..utils import pre_configs
from ..utils.call_func import CallFunc
from .bottle import Bottle, ServerAdapter, request, HTTPResponse, response, BaseRequest
from .cmd_server import CmdServer
from . import ocr_server

BaseRequest.MEMFILE_MAX = 10485760  # 设置单次请求大小上限：10MB

UmiWeb = Bottle()
Host = "127.0.0.1"  # 由qml设置


# 允许跨域
@UmiWeb.hook("before_request")
def _validate_before():
    re_method = request.environ.get("REQUEST_METHOD")
    hacrm = request.environ.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD")
    if re_method == "OPTIONS" and hacrm:
        request.environ["REQUEST_METHOD"] = hacrm


@UmiWeb.hook("after_request")
def _validate_after():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"


# ============================== 基础路由 ==============================


@UmiWeb.route("/")
@UmiWeb.route("/umiocr")
def _umiocr():
    from umi_about import UmiAbout  # 项目信息

    return UmiAbout["fullname"]


# 跨进程接收命令行参数
@UmiWeb.route("/argv", method="POST")
def _argv():
    addr = request.environ.get("REMOTE_ADDR")
    if addr == "127.0.0.1":
        data = request.json
        res = CmdServer.execute(data)
        return res
    else:
        msg = "Unauthorized access. Only local requests are allowed.\n此接口只允许本机访问。"
        return HTTPResponse(msg, status=401)


ocr_server.init(UmiWeb)

# =============== 自定义服务器适配器，方便控制服务终止 ==============================
QmlCallback = None  # qml回调函数


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
        self.port = pre_configs.getValue("server_port")  # 提取记录的端口号
        self.host = Host
        # 找到一个可用的端口号
        while True:
            try:
                self.server = make_server(
                    self.host,
                    self.port,
                    handler,
                    server_class=self.CustomWSGIServer,
                    **self.options,
                )
                break
            except OSError:  # 当前端口号已占用，测试下一位端口号
                print(f"[Warning] 服务器端口号{self.port}已被占用")
                self.port += 1
                if self.port > 65535:
                    self.port = 1024
                pre_configs.setValue("server_port", self.port)  # 写入记录

        print("Listening on http://%s:%d/\n" % (self.host, self.port))
        CallFunc.now(QmlCallback, self.port)  # 在主线程中调用回调函数，告知实际端口号
        self.server.serve_forever()

    def stop(self):  # 服务终止
        # self.server.server_close() # 备选方案，但会导致 bad fd 异常
        print("###  WEB服务器准备关闭！")
        self.server.close_all_request()  # 强制关闭客户端连接
        self.server.shutdown()  # 关闭服务器
        print("###  WEB服务器已关闭！")


# ============================== 线程类 ==============================
class _WorkerClass(QRunnable):
    def run(self):
        self._server = _WSGIRefServer()
        UmiWeb.run(server=self._server)


_Worker = _WorkerClass()


# ============================== 控制接口 ==============================


# 启动web服务。传入qml对象，回调函数名，主机地址
def runUmiWeb(qmlObj, callback, host):
    global QmlCallback, Host
    Host = host
    QmlCallback = getattr(qmlObj, callback, None)  # 提取qml回调函数
    threadPool = QThreadPool.globalInstance()  # 获取全局线程池
    threadPool.start(_Worker)  # 启动服务器线程


# 切换端口号（下次启动生效）
def setPort(port):
    pre_configs.setValue("server_port", port)
