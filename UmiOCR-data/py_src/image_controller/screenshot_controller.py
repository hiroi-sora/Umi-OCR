# ========================================
# =============== 截图控制 ===============
# ========================================

from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..utils.utils import findImages

import time
from PySide2.QtGui import QGuiApplication, QClipboard, QImage, QPixmap  # 截图 剪贴板

Clipboard = QClipboard()  # 剪贴板


class _ScreenshotControllerClass:
    # 延时wait秒后，获取所有屏幕的截图，返回imgID
    def getScreenshot(self, wait=0):
        if wait > 0:
            time.sleep(wait)
        try:
            grabList = []
            screensList = QGuiApplication.screens()
            for screen in screensList:
                pixmap = screen.grabWindow(0)  # 截图
                imgID = PixmapProvider.addPixmap(pixmap)  # 存入提供器，获取imgID
                grabList.append(
                    {
                        "imgID": imgID,
                        "screenName": screen.name(),
                    }
                )
            return grabList
        except Exception as e:
            return [f"[Error] Screenshot: {e}"]

    # 对一张图片做裁切。传入原图imgID和裁切参数，返回裁切后的imgID或[Error]
    def getClipImgID(self, imgID, x, y, w, h):
        pixmap = PixmapProvider.getPixmap(imgID)
        if not pixmap:
            e = f'[Error] ScreenshotOCR: Key "{imgID}" does not exist in the PixmapProvider dict.'
            return e
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            e = f"[Error] ScreenshotOCR: x/y/w/h value error. {x}/{y}/{w}/{h}"
            return e
        pixmap = pixmap.copy(x, y, w, h)  # 进行裁切
        clipID = PixmapProvider.addPixmap(pixmap)  # 存入提供器，获取imgID
        return clipID

    # 获取当前剪贴板的内容
    # type: imgID paths text
    def getPaste(self):
        # 获取剪贴板数据
        mimeData = Clipboard.mimeData()
        res = {"type": ""}  # 结果字典
        # 检查剪贴板的内容，若是图片，则提取它并扔给OCR
        if mimeData.hasImage():
            image = Clipboard.image()
            pixmap = QPixmap.fromImage(image)
            pasteID = PixmapProvider.addPixmap(pixmap)  # 存入提供器
            res = {"type": "imgID", "imgID": pasteID}
        # 若为URL
        elif mimeData.hasUrls():
            urlList = mimeData.urls()
            paths = []
            for url in urlList:  # 遍历URL列表，提取其中的文件
                if url.isLocalFile():
                    p = url.toLocalFile()
                    paths.append(p)
            paths = findImages(paths, False)  # 过滤，保留图片的路径
            if len(paths) == 0:  # 没有有效图片
                res = {"type": "error", "error": "[Warning] No image in clipboard."}
            else:  # 将有效图片地址传入OCR，返回地址列表
                res = {"type": "paths", "paths": paths}
        elif mimeData.hasText():
            text = mimeData.text()
            res = {"type": "text", "text": text}
        else:
            res = {"type": "error", "error": "[Warning] Unknow mimeData in clipboard."}
        return res  # 返回结果字典


ScreenshotController = _ScreenshotControllerClass()
