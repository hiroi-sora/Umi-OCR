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
        print("截图完毕！！！", argd)
