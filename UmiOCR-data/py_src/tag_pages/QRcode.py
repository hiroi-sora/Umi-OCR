# =======================================
# =============== 二维码页 ===============
# =======================================

from .page import Page  # 页基类
from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..utils.utils import findImages
from ..mission.simple_mission import SimpleMission

from PySide2.QtGui import QGuiApplication, QClipboard, QImage, QPixmap  # 截图 剪贴板
import time
import pyzbar.pyzbar as pyzbar


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
        print("处理：", msn)
        time.sleep(1)
        imgID = imgPath = ""
        if "imgID" in msn:
            imgID = msn["imgID"]
        elif "path" in msn:
            imgPath = msn["path"]
        t2 = time.time()
        res = {
            "code": 100,
            "time": t2 - t1,
            "timestamp": t2,
            "data": [
                {
                    "box": [[0, 0], [0, 0], [0, 0], [0, 0]],
                    "score": 1,
                    "text": "11111",
                }
            ],
        }
        self.callQmlInMain("onQRcodeGet", res, imgID, imgPath)  # 在主线程中调用qml
