# 全局设置连接器

from . import app_opengl
from .i18n import I18n
from .shortcut import ShortcutApi
from ..server.web_server import runUmiWeb

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

    # 启动web服务器，port端口
    @Slot(int)
    def runUmiWeb(self, port):
        runUmiWeb(port)
