# ==========================================================
# =============== Python向Qml传输 Pixmap 图像 ===============
# ==========================================================

from . import ImageQt
from urllib.parse import unquote
from ..platform import Platform

from PySide2.QtCore import Qt, QByteArray, QBuffer
from PySide2.QtGui import QPixmap, QImage, QPainter, QClipboard
from PySide2.QtQuick import QQuickImageProvider
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
            self._delCompCache(compID, imgID)  # 先清缓存
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
            return ImageQt.fromqimage(im)
        except Exception as e:
            print(f"[Error] QPixmap 转 PIL 失败：{e}")
            return None

    # py将PIL对象写回pixmapDict。主要是记录预处理的图像
    # imgID可以已存在，也可以新添加
    def setPilImage(self, img, imgID=""):
        try:
            pixmap = ImageQt.toqpixmap(img)
        except Exception as e:
            e = f"[Error] PIL 转 QPixmap 失败：{e}"
            print(e)
            return e
        if not imgID:
            imgID = str(uuid4())
        self.pixmapDict[imgID] = pixmap
        return imgID

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
        image.save(buffer, "PNG")  # 将 QImage 保存为字节数组
        buffer.close()
        bytesData = byteArray.data()  # 获取字节数组的内容
        return bytesData

    # 清空一个组件的缓存。imgID可选该组件下一次更新的图片ID。
    def _delCompCache(self, compID, imgID=""):
        if compID in self.compDict:
            last = self.compDict[compID]
            if imgID and imgID == last:
                print(f"[Warning] 图片组件异常清理： {compID} {imgID}")
                return  # 如果下一次更新的ID等于当前ID，则为异常，不进行清理
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


# 读入一张图片，返回该图片
# type: pixmap / qimage / error
def _imread(path):
    path = unquote(path)  # 做一次URL解码
    if path.startswith("image://pixmapprovider/"):
        path = path[23:]
        if "/" in path:
            compID, imgID = path.split("/", 1)
            if imgID in PixmapProvider.pixmapDict:
                return {"type": "pixmap", "data": PixmapProvider.pixmapDict[imgID]}
        else:
            return {"type": "error", "data": f"[Warning] ID not in pixmapDict: {path}"}
    elif path.startswith("file:///"):
        path = path[8:]
        if os.path.exists(path):
            try:
                image = QImage(path)
                return {"type": "qimage", "data": image, "path": path}
            except Exception as e:
                return {
                    "type": "error",
                    "data": f"[Error] QImage cannot read path: {path}",
                }
        else:
            return {"type": "error", "data": f"[Warning] Path {path} not exists."}
    elif path in PixmapProvider.pixmapDict:
        return {"type": "pixmap", "data": PixmapProvider.pixmapDict[path]}
    elif os.path.exists(path):
        try:
            image = QImage(path)
            return {"type": "qimage", "data": image, "path": path}
        except Exception as e:
            return {"type": "error", "data": f"[Error] QImage cannot read path: {path}"}
    return {"type": "error", "data": f"[Warning] Unknow: {path}"}


# 复制一张图片到剪贴板
def copyImage(path):
    im = _imread(path)
    typ, data = im["type"], im["data"]
    if typ == "error":
        return data
    try:
        if typ == "pixmap":
            Clipboard.setPixmap(data)
        elif typ == "qimage":
            Clipboard.setImage(data)
        return "[Success]"
    except Exception as e:
        return f"[Error] can't copy: {e}\n{path}"


# 用系统默认应用打开图片
def openImage(path):
    im = _imread(path)
    typ, data = im["type"], im["data"]
    if typ == "error":
        return data
    # 若原本为本地图片，则直接打开
    if "path" in im:
        path = im["path"]
    # 若为内存数据，则创建缓存文件
    else:
        path = f"umi_temp_image.png"
        try:
            if typ == "pixmap":
                data = data.toImage()
            data.save(path)
            print("== 保存临时文件")
        except Exception as e:
            return f"[Error] can't save to temp file: {e}\n{path}"
    # 打开文件
    try:
        Platform.startfile(path)
        return "[Success]"
    except Exception as e:
        return f"[Error] can't open image: {e}\n{path}"


# 保存一张图片
def saveImage(fromPath, toPath):
    if toPath.startswith("file:///"):
        toPath = toPath[8:]
    im = _imread(fromPath)
    typ, data = im["type"], im["data"]
    if typ == "error":
        return data
    try:
        if typ == "pixmap":
            data.save(toPath)
        elif typ == "qimage":
            data.save(toPath)
        return f"[Success] {toPath}"
    except Exception as e:
        return f"[Error] can't save: {e}\n{fromPath}\n{toPath}"
