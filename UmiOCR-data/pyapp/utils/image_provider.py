# ==========================================================
# =============== Python向Qml传输 Pixmap 图像 ===============
# ==========================================================

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QPainter
from PySide2.QtQuick import QQuickImageProvider
from uuid import uuid4  # 唯一ID


# Pixmap型图片提供器
class PixmapProviderClass(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Pixmap)
        self.pixmapDict = {}  # 存放所有pixmap的字典

    # 向qml返回图片
    def requestPixmap(self, imgID, size, resSize):
        if imgID not in self.pixmapDict:
            print(f"【Error】请求Pixmap，传入不存在的imgID：{imgID}")
            pixmap = QPixmap(1, 100)
            pixmap.fill(Qt.blue)
            painter = QPainter(pixmap)  # 绘制警告条纹
            painter.setPen(Qt.red)
            painter.drawLine(0, 0, 0, 5)
            painter.drawLine(0, 95, 0, 100)
            return pixmap
        return self.pixmapDict[imgID]

    # 添加一个Pixmap图片到提供器，返回imgID
    def addPixmap(self, pixmap):
        imgID = str(uuid4())
        self.pixmapDict[imgID] = pixmap
        return imgID


# 图片提供器 单例
PixmapProvider = PixmapProviderClass()
