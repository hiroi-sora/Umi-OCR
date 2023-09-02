# 通用工具类

from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtGui import QClipboard

Clipboard = QClipboard()  # 剪贴板


class UtilsConnector(QObject):
    def __init__(self):
        super().__init__()

    # 将文本写入剪贴板
    @Slot(str)
    def copyText(self, text):
        Clipboard.setText(text)
