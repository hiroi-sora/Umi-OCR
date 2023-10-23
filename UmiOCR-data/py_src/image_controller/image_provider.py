# ==========================================================
# =============== Python向Qml传输 Pixmap 图像 ===============
# ==========================================================

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QImage, QPainter, QClipboard
from PySide2.QtCore import QByteArray, QBuffer, QIODevice
from PySide2.QtQuick import QQuickImageProvider
from io import BytesIO
from PIL import Image
from uuid import uuid4  # 唯一ID
import os

Clipboard = QClipboard()  # 剪贴板


# Pixmap型图片提供器
class PixmapProviderClass(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Pixmap)
        self.pixmapDict = {}  # 缓存所有pixmap的字典
        self.compDict = {}  # 缓存所有组件的字典
        # 空图占位符
        self._noneImg = None

    # 向qml返回图片，imgID不存在时返回警告图
    def requestPixmap(self, path, size=None, resSize=None):
        if "/" in path:
            compID, imgID = path.split("/", 1)
            self._delCompCache(compID)  # 先清缓存
            if imgID in self.pixmapDict:
                self.compDict[compID] = imgID  # 记录缓存
                return self.pixmapDict[imgID]
        else:  # 清空一个组件的缓存
            self._delCompCache(path)
        return self._getNoneImg()  # 返回占位符

    # 添加一个Pixmap图片到提供器，返回imgID
    def addPixmap(self, pixmap):
        imgID = str(uuid4())
        self.pixmapDict[imgID] = pixmap
        return imgID

    # 向py返回图片，相当于requestPixmap，但imgID不存在时返回None
    def getPixmap(self, imgID):
        return self.pixmapDict.get(imgID, None)

    # 向py返回PIL对象
    def getPilImage(self, imgID):
        im = self.getPixmap(imgID)
        if not im:
            return None
        try:
            buffer = QBuffer()
            qt_openmode = QIODevice
            buffer.open(qt_openmode.ReadWrite)
            # 若是png，则保留alpha通道。否则ppm兼容性更好。
            if im.hasAlphaChannel():
                im.save(buffer, "png")
            else:
                im.save(buffer, "ppm")
            b = BytesIO()
            b.write(buffer.data())
            buffer.close()
            b.seek(0)
            return Image.open(b)
        except Exception as e:
            print(f"[Error] QPixmap 转 PIL 失败：{e}")
            return None

    # 从pixmapDict缓存中删除一个或一批图片
    # 一般无需手动调用此函数！缓存会自动管理、清除。
    def delPixmap(self, imgIDs):
        if type(imgIDs) == str:
            imgIDs = [imgIDs]
        for i in imgIDs:
            if i in self.pixmapDict:
                del self.pixmapDict[i]
        print(f"删除图片缓存，剩余：{len(self.pixmapDict)}")

    # 将 QPixmap 或 QImage 转换为字节
    @staticmethod
    def toBytes(image):
        if isinstance(image, QPixmap):
            image = image.toImage()
        elif not isinstance(image, QImage):
            raise ValueError(
                f"[Error] Only QImage or QPixmap can toBytes(), no {str(type(image))}."
            )
        byteArray = QByteArray()  # 创建一个字节数组
        buffer = QBuffer(byteArray)  # 创建一个缓冲区
        buffer.open(QBuffer.WriteOnly)
        image.save(buffer, "JPEG")  # 将 QImage 保存为字节数组
        buffer.close()
        bytesData = byteArray.data()  # 获取字节数组的内容
        return bytesData

    # 清空一个组件的缓存
    def _delCompCache(self, compID):
        if compID in self.compDict:
            last = self.compDict[compID]
            if last in self.pixmapDict:
                del self.pixmapDict[last]
            del self.compDict[compID]

    # 返回空图占位符
    def _getNoneImg(self):
        if self._noneImg:
            return self._noneImg
        pixmap = QPixmap(1, 100)
        pixmap.fill(Qt.blue)
        painter = QPainter(pixmap)  # 绘制警告条纹
        painter.setPen(Qt.red)
        painter.drawLine(0, 0, 0, 5)
        painter.drawLine(0, 95, 0, 100)
        self._noneImg = pixmap
        return self._noneImg


# 图片提供器 单例
PixmapProvider = PixmapProviderClass()


# 复制一张图片到剪贴板
def copyImage(path):
    if path.startswith("image://pixmapprovider/"):
        path = path[23:]
        if path in PixmapProvider.pixmapDict:
            Clipboard.setPixmap(PixmapProvider.pixmapDict[path])
            return "[Success]"
        else:
            return f"[Warning] ID {path} not in pixmapDict."
    elif path.startswith("file:///"):
        path = path[8:]
        if os.path.exists(path):
            image = QImage(path)
            Clipboard.setImage(image)
            return "[Success]"
        else:
            return f"[Warning] Path {path} not exists."

    if path in PixmapProvider.pixmapDict:
        Clipboard.setPixmap(PixmapProvider.pixmapDict[path])
        return "[Success]"
    if os.path.exists(path):
        image = QImage(path)
        Clipboard.setImage(image)
        return "[Success]"
    return f"[Warning] Unknow: {path}"
