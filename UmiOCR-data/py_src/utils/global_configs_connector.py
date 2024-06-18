# 全局设置连接器

from . import app_opengl
from .i18n_configs import I18n
from ..platform import Platform
from .pre_configs import getErrorStr
from ..server import web_server
from ..server.cmd_server import CmdActuator

import os
from PySide2.QtCore import QObject, Slot, Signal


class GlobalConfigsConnector(QObject):
    def __init__(self):
        super().__init__()

    # 创建快捷方式
    @Slot(str, result=str)
    def createShortcut(self, position):
        return Platform.Shortcut.createShortcut(position)

    # 删除快捷方式
    @Slot(str, result=int)
    def deleteShortcut(self, position):
        return Platform.Shortcut.deleteShortcut(position)

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
    @Slot("QVariant", str, str, result=int)
    def runUmiWeb(self, qmlObj, callback, host):
        web_server.runUmiWeb(qmlObj, callback, host)

    # 设置服务端口号
    @Slot(int)
    def setServerPort(self, port):
        web_server.setPort(port)

    # 将qml模块字典传入cmd执行器
    @Slot("QVariant")
    def setQmlToCmd(self, moduleDict):
        CmdActuator.initCollect(moduleDict)

    # 检查权限，返回检查结果
    @Slot(result=str)
    def checkAccess(self):
        cwd = os.getcwd()  # 当前工作路径
        err = getErrorStr()  # 读写异常情况
        if not err:  # 没有异常，则再检查一遍权限
            if not os.access(cwd, os.R_OK):
                err += "在当前路径不具有可读权限。\nDo not have read permission on the current path."
            if not os.access(cwd, os.W_OK):
                err += (
                    "在当前路径不具有可写权限。\nDo not have write permission on the current path."
                )
        if err:
            err = cwd + "\n" + err
        return err
