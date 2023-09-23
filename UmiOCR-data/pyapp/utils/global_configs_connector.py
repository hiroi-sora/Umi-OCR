# 全局设置连接器

from . import app_opengl
from .i18n import I18n
from .shortcut import ShortcutApi
from ..server import web_server
from ..server.cmd_server import CmdActuator

from PySide2.QtCore import QObject, Slot, Signal


class GlobalConfigsConnector(QObject):
    def __init__(self):
        super().__init__()

    # 创建快捷方式
    @Slot(str, result=bool)
    def createShortcut(self, position):
        return ShortcutApi.createShortcut(position)

    # 删除快捷方式
    @Slot(str, result=int)
    def deleteShortcut(self, position):
        return ShortcutApi.deleteShortcut(position)

    # 获取UI语言信息
    @Slot(result="QVariant")
    def i18nGetInfos(self):
        return I18n.getInfos()

    # 设置UI语言
    @Slot(str, result=bool)
    def i18nSetLanguage(self, lang):
        return I18n.setLanguage(lang)

    # 获取Opengl渲染器选项
    @Slot(result=str)
    def getOpengl(self):
        return app_opengl.getOpengl()

    # 设置Opengl渲染器选项
    @Slot(str)
    def setOpengl(self, opt):
        app_opengl.setOpengl(opt)

    # 启动web服务器，传入qml对象及回调函数名。
    @Slot("QVariant", str, result=int)
    def runUmiWeb(self, qmlObj, callback):
        web_server.runUmiWeb(qmlObj, callback)

    # 设置服务端口号
    @Slot(int)
    def setServerPort(self, port):
        web_server.setPort(port)

    # 将qml模块字典传入cmd执行器
    @Slot("QVariant")
    def setQmlToCmd(self, moduleDict):
        CmdActuator.initCollect(moduleDict)
