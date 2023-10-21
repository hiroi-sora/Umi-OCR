# 通用工具连接器

from . import utils
from ..platform import Platform  # 跨平台

from PySide2.QtCore import QObject, Slot, Signal


class UtilsConnector(QObject):
    def __init__(self):
        super().__init__()

    # 将文本写入剪贴板
    @Slot(str)
    def copyText(self, text):
        utils.copyText(text)

    # 用系统应用打开文件或目录
    @Slot(str)
    def startfile(self, path):
        Platform.startfile(path)

    # QUrl列表 转 String列表
    @Slot("QVariant", result="QVariant")
    def QUrl2String(self, fileUrls):
        return utils.QUrl2String(fileUrls)
