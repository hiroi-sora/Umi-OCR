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
        mainRatio = -1  # 主屏幕缩放
        for screen in screensList:
            # 截图
            pixmap = screen.grabWindow(0)
            imgID = PixmapProvider.addPixmap(pixmap)
            # 获取屏幕缩放比
            sysRatio = screen.devicePixelRatio()  # 系统缩放比
            relativeRatio = 1.0  # 相对主屏幕缩放比
            if mainRatio == -1:  # 主屏幕
                mainRatio = sysRatio
            else:  # 非主屏幕
                relativeRatio = sysRatio / mainRatio
            geom = screen.geometry()
            geometry = {
                # 逻辑坐标
                "x": geom.x(),
                "y": geom.y(),
                "width": geom.width(),
                "height": geom.height(),
                # 缩放比
                "relativeRatio": relativeRatio,
            }
            grabList.append({"imgID": imgID, "geometry": geometry})
            print("缩放：", relativeRatio)
        # return []
        return grabList
