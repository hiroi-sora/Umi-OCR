# 图片处理连接器

from .image_provider import copyImage

from PySide2.QtCore import QObject, Slot, Signal


class ImgConnector(QObject):
    # 将图片写入剪贴板，返回成功与否
    @Slot(str, result=str)
    def copyImage(self, path):
        return copyImage(path)
