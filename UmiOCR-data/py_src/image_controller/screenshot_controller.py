# ========================================
# =============== 截图控制 ===============
# ========================================

from ..image_controller.image_provider import PixmapProvider  # 图片提供器

import time
from PySide2.QtGui import QGuiApplication, QClipboard, QImage, QPixmap  # 截图 剪贴板


class _ScreenshotControllerClass:
    def __init__(self):
        self._cacheIDs = []  # 缓存截图中的imgID

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
                self._cacheIDs.append(imgID)  # 存入缓存
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
        self.clearCache()  # 清缓存
        return clipID

    # 清理缓存
    def clearCache(self):
        PixmapProvider.delPixmap(self._cacheIDs)
        self._cacheIDs = []


ScreenshotController = _ScreenshotControllerClass()
