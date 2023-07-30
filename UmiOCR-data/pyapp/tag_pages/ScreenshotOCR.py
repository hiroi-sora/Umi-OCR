# ========================================
# =============== 截图OCR页 ===============
# ========================================

from .page import Page  # 页基类
from ..utils.image_provider import PixmapProvider  # 图片提供器

from PySide2.QtGui import QGuiApplication  # 截图


class ScreenshotOCR(Page):
    # ========================= 【qml调用python】 =========================

    def screenshot(self):
        print("PY 截图！")
        screensList = QGuiApplication.screens()
        grabList = []
        for screen in screensList:
            pixmap = screen.grabWindow(0)
            imgID = PixmapProvider.addPixmap(pixmap)
            geom = screen.geometry()
            geometry = {
                "x": geom.x(),
                "y": geom.y(),
                "w": geom.width(),
                "h": geom.height(),
            }
            grabList.append({"imgID": imgID, "geometry": geometry})
        return grabList
