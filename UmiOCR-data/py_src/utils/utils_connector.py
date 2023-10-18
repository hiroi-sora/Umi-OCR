# 通用工具连接器

from . import utils
from .image_provider import copyImage
from ..platform import Platform  # 跨平台

from PySide2.QtCore import QObject, Slot, Signal


class UtilsConnector(QObject):
    def __init__(self):
        super().__init__()

    # 将文本写入剪贴板
    @Slot(str)
    def copyText(self, text):
        utils.copyText(text)

    # 将图片写入剪贴板，返回成功与否
    @Slot(str, result=str)
    def copyImage(self, path):
        return copyImage(path)

    # 用系统应用打开文件或目录
    @Slot(str)
    def startfile(self, path):
        Platform.startfile(path)
