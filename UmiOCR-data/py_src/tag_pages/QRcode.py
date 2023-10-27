# =======================================
# =============== 二维码页 ===============
# =======================================

from .page import Page  # 页基类
from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..mission.simple_mission import SimpleMission

import os
import time
from PIL import Image, ImageEnhance, ImageFilter


class QRcode(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.recentResult = None  # 缓存最后一次识别结果
        self._configDict = None
        self._simpleMission = SimpleMission(self._scanQRcode)

    # 对一个imgID进行扫码
    def scanImgID(self, imgID, configDict):
        self.recentResult = None
        self._configDict = configDict
        self._simpleMission.addMissionList([{"imgID": imgID}])

    # 对一串path进行扫码
    def scanPaths(self, paths, configDict):
        self.recentResult = None
        self._configDict = configDict
        msnList = [{"path": x} for x in paths]
        self._simpleMission.addMissionList(msnList)

    # ========================= 【扫码处理】 =========================

    # 扫码
    def _scanQRcode(self, msn):
        try:
            import pyzbar.pyzbar as pyzbar
        except Exception as e:
            e = str(e)
            if "libiconv.dll" in e:
                return {
                    "code": 901,
                    "data": f"【Error】二维码解析器 pyzbar 未能加载 libiconv.dll 。请尝试安装 Microsoft Visual C++运行库后重试。\n[Error] Pyzbar failed to load libiconv.dll. Please try installing the Microsoft Visual C++ runtime and try again.\n{e}",
                }
            return {
                "code": 902,
                "data": f"【Error】无法导入二维码解析器 pyzbar 。\n[Error] Unable to import pyzbar.\n{e}",
            }
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
                # 预处理
                img = self._preprocessing(img, imgID)
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
            res["data"] = f"【Error】二维码解析失败。\n[Error] QRcode failed. {e}"
        t2 = time.time()
        res["time"] = t2 - t1
        res["timestamp"] = t2
        self.callQmlInMain("onQRcodeGet", res, imgID, imgPath)  # 在主线程中调用qml

    # 图像预处理，传入PIL对象
    def _preprocessing(self, img, imgID):
        flag = False
        c = self._configDict
        s = round(c["preprocessing.median_filter_size"])
        if s > 0 and s % 2 == 1:
            img = img.filter(ImageFilter.MedianFilter(size=s))
            flag = True
        if c["preprocessing.sharpness_factor"] > 0:
            img = ImageEnhance.Sharpness(img).enhance(
                c["preprocessing.sharpness_factor"]
            )
            flag = True
        if c["preprocessing.contrast_factor"] > 0:
            img = ImageEnhance.Contrast(img).enhance(c["preprocessing.contrast_factor"])
            flag = True
        if c["preprocessing.grayscale"]:
            img = img.convert("L")
            flag = True
            if c["preprocessing.threshold"] > -1:
                t = round(c["preprocessing.threshold"])
                img = img.point(lambda p: p > t and 255)
        # if flag and imgID:  # 写回
        #     PixmapProvider.setPilImage(img, imgID)
        return img
