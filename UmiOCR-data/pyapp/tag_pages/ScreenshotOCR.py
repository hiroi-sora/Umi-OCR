# ========================================
# =============== 截图OCR页 ===============
# ========================================

from .page import Page  # 页基类
from ..utils.image_provider import PixmapProvider  # 图片提供器

from PySide2.QtGui import QGuiApplication  # 截图


class ScreenshotOCR(Page):
    # ========================= 【qml调用python】 =========================

    def screenshot(self):  # 开始截图
        screensList = QGuiApplication.screens()
        grabList = []
        for screen in screensList:
            pixmap = screen.grabWindow(0)  # 截图
            imgID = PixmapProvider.addPixmap(pixmap)  # 存入提供器，获取imgID
            grabList.append(
                {  # 传递信息给qml
                    "imgID": imgID,
                    "screenName": screen.name(),
                }
            )
        return grabList

    # 截图完毕，提交OCR，并返回裁切结果
    def screenshotEnd(self, argd):
        pixmap = PixmapProvider.getPixmap(argd["imgID"])
        if not pixmap:
            e = f'[Error] ScreenshotOCR: Key "{argd["imgID"]}" does not exist in the PixmapProvider dict.'
            return e
        x, y, w, h = argd["clipX"], argd["clipY"], argd["clipW"], argd["clipH"]
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            e = f"[Error] ScreenshotOCR: x/y/w/h value error. {x}/{y}/{w}/{h}"
            return e
        pixmap = pixmap.copy(x, y, w, h)  # 进行裁切
        clipID = PixmapProvider.addPixmap(pixmap)  # 存入提供器，获取imgID
        if "allImgID" in argd:  # 删除完整图片的缓存
            PixmapProvider.delPixmap(argd["allImgID"])
        return clipID

    # ====================================================================
