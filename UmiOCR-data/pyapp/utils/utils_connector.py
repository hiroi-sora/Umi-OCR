# 通用工具连接器

from . import utils
from .shortcut import ShortcutApi

from PySide2.QtCore import QObject, Slot, Signal


class UtilsConnector(QObject):
    def __init__(self):
        super().__init__()

    # 将文本写入剪贴板
    @Slot(str)
    def copyText(self, text):
        utils.copyText(text)

    # 创建快捷方式
    @Slot(str, result=bool)
    def createShortcut(self, position):
        return ShortcutApi.createShortcut(position)

    # 删除快捷方式
    @Slot(str, result=int)
    def deleteShortcut(self, position):
        return ShortcutApi.deleteShortcut(position)
