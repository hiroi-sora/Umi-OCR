# 通用工具连接器

from . import utils
from . import theme_provider
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

    # 获取主题
    @Slot(result="QVariant")
    def getThemes(self):
        return theme_provider.getThemes()

    # 设置主题
    @Slot("QVariant")
    def setThemes(self, tdict):
        theme_provider.setThemes(tdict)
