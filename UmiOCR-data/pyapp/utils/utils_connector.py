# 通用工具类
from . import utils

from PySide2.QtCore import QObject, Slot, Signal


class UtilsConnector(QObject):
    def __init__(self):
        super().__init__()

    # 将文本写入剪贴板
    @Slot(str)
    def copyText(self, text):
        utils.copyText(text)
