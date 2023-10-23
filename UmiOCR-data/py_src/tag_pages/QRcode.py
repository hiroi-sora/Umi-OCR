# =======================================
# =============== 二维码页 ===============
# =======================================

from .page import Page  # 页基类
from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..mission.simple_mission import SimpleMission

from PySide2.QtGui import QGuiApplication, QClipboard, QImage, QPixmap  # 截图 剪贴板
import os
import time
import pyzbar.pyzbar as pyzbar
from PIL import Image, ImageEnhance
from PySide2.QtCore import QBuffer, QIODevice  # qt图像转PIL图像
from io import BytesIO

Clipboard = QClipboard()  # 剪贴板


class QRcode(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.recentResult = None  # 缓存最后一次识别结果
        self._simpleMission = SimpleMission(self._scanQRcode)

    # 对一个imgID进行扫码
    def scanImgID(self, imgID, configDict):
        self.recentResult = None
        self._simpleMission.addMissionList([{"imgID": imgID}])

    # 对一串path进行扫码
    def scanPaths(self, paths, configDict):
        self.recentResult = None
        msnList = [{"path": x} for x in paths]
        self._simpleMission.addMissionList(msnList)

    # ========================= 【扫码处理】 =========================

    # 扫码
    def _scanQRcode(self, msn):
        t1 = time.time()
        imgID = imgPath = ""
        if "imgID" in msn:
            imgID = msn["imgID"]
        elif "path" in msn:
            imgPath = msn["path"]
        res = {
            "code": 101,
            "data": "QR code not recognized in the image.",
        }
        try:
            img = None
            # 读入路径或qpixmap，转为PIL对象
            if "imgID" in msn:
                img = PixmapProvider.getPilImage(imgID)
            elif "path" in msn:
                res["fileName"] = os.path.basename(imgPath)
                img = Image.open(imgPath)
            if img:
                # TODO：预处理
                # 二维码识别
                codes = pyzbar.decode(img)
                if codes:
                    data = []
                    for c in codes:
                        data.append(
                            {
                                "box": [
                                    [c.polygon[0].x, c.polygon[0].y],
                                    [c.polygon[3].x, c.polygon[3].y],
                                    [c.polygon[2].x, c.polygon[2].y],
                                    [c.polygon[1].x, c.polygon[1].y],
                                ],
                                "score": 1,
                                "text": c.data.decode("utf-8"),
                            }
                        )
                    res["code"] = 100
                    res["data"] = data
        except Exception as e:
            res["code"] = 102
            res["data"] = f"QRcode failed. {e}"
        t2 = time.time()
        res["time"] = t2 - t1
        res["timestamp"] = t2
        self.callQmlInMain("onQRcodeGet", res, imgID, imgPath)  # 在主线程中调用qml
