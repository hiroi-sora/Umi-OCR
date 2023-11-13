# =======================================
# =============== 二维码页 ===============
# =======================================

from .page import Page  # 页基类
from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..mission.simple_mission import SimpleMission

import os
import time
from PIL import Image, ImageEnhance, ImageFilter
import base64

try:
    import zxingcpp
except Exception as e:
    zxingcpp = None
    zxingcppErr = str(e)


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

    # 生成二维码
    # format: "Aztec","Codabar","Code128","Code39","Code93","DataBar","DataBarExpanded","DataMatrix","EAN13","EAN8","ITF","LinearCodes","MatrixCodes","MaxiCode","MicroQRCode","PDF417","QRCode","UPCA","UPCE",
    # quiet_zone: 四周的空闲区域
    # ec_level：纠错等级，-1 - 自动, 1- L-7% , 0 - M-15%, 3 - Q-25%, 2 - H-30%
    # 纠错仅用于Aztec、PDF417和QRCode
    def writeBarcode(self, format, text, w=0, h=0, quiet_zone=-1, ec_level=-1):
        # 转整数
        w, h = round(w), round(h)
        quiet_zone, ec_level = round(quiet_zone), round(ec_level)
        # 生成格式对象
        bFormat = getattr(zxingcpp.BarcodeFormat, format, None)
        if not bFormat:
            return f"[Error] format {format} not in zxingcpp.BarcodeFormat!"
        try:
            bit = zxingcpp.write_barcode(bFormat, text, w, h, quiet_zone, ec_level)
        except Exception as e:
            return f"[Error] [{format}] {e}"
        try:
            img = Image.fromarray(bit, "L")
        except Exception as e:
            return f"[Error] Image.fromarray: {e}"
        imgID = PixmapProvider.setPilImage(img)
        # 若 setPilImage 失败， imgID.startswith("[Error]")
        return imgID

    # ========================= 【扫码处理】 =========================

    # 解析 zxingcpp 库的返回结果，转为字典。此函数允许发生异常。
    # 失败返回值： {"code":错误码, "data": "错误信息字符串"}
    # 成功返回值： {"code":100, "data": [每个码的数据] }
    # data: {"box":[包围盒], "score":1, "text": "文本"}
    def _zxingcpp2dict(self, codes):
        # 图中无码
        if not codes:
            return {
                "code": 101,
                "data": "QR code not found in the image.",
            }
        # 处理结果冲每一个二维码
        data = []
        for c in codes:
            if not c.valid:  # 码无效
                continue
            d = {}
            # 方向
            d["orientation"] = c.orientation
            # 位置
            d["box"] = [
                [c.position.top_left.x, c.position.top_left.y],
                [c.position.top_right.x, c.position.top_right.y],
                [c.position.bottom_right.x, c.position.bottom_right.y],
                [c.position.bottom_left.x, c.position.bottom_left.y],
            ]
            d["score"] = 1  # 置信度，兼容OCR格式，无意义
            # 内容为文本类型
            if c.content_type.name == "Text":
                d["text"] = c.text
            # 内容为其它格式
            # TODO: 现在是通用的处理方法，将二进制内容转为纯文本或base64
            # 或许对于某些格式的码，有更好的转文本方式
            else:
                text = f"type: {c.content_type.name}\ndata: "
                try:
                    # 尝试将 bytes 转换为纯文本字符串
                    t = c.bytes.decode("utf-8")
                    text += t
                except UnicodeDecodeError:
                    # 如果无法直接转换为纯文本，则使用 Base64 编码输出结果
                    t = base64.b64encode(c.bytes)
                    text += "[Base64]\n" + t.decode("utf-8")
                d["text"] = text
            data.append(d)
        if data:
            return {
                "code": 100,
                "data": data,
            }
        else:
            l = len(codes)
            return {
                "code": 102,
                "data": f"【Error】{l}组二维码解码失败。\nFailed to decode {l} sets of QR codes.",
            }

    # 扫码
    def _scanQRcode(self, msn):
        imgID = imgPath = ""
        t1 = time.time()

        def _run():
            nonlocal imgID, imgPath
            # 导入库失败
            if not zxingcpp:
                return {
                    "code": 901,
                    "data": f"【Error】无法导入二维码解析器 zxingcpp 。\n[Error] Unable to import zxingcpp.\n{zxingcppErr}",
                }
            # 读入图片
            try:
                if "imgID" in msn:
                    imgID = msn["imgID"]
                    img = PixmapProvider.getPilImage(imgID)
                elif "path" in msn:
                    imgPath = msn["path"]
                    img = Image.open(imgPath)
            except Exception as e:
                return {
                    "code": 202,
                    "data": f"【Error】图片读取失败。\n[Error] Image reading failed.\n {e}",
                }
            # 预处理
            try:
                img = self._preprocessing(img, imgID)
            except Exception as e:
                return {
                    "code": 203,
                    "data": f"【Error】图片预处理失败。\n[Error] Image preprocessing failed.\n {e}",
                }
            # 二维码解析
            try:
                codes = zxingcpp.read_barcodes(img)
            except Exception as e:
                return {
                    "code": 204,
                    "data": f"【Error】zxingcpp 二维码解析失败。\n[Error] zxingcpp read_barcodes failed.\n {e}",
                }
            # 结果解析
            try:
                return self._zxingcpp2dict(codes)
            except Exception as e:
                return {
                    "code": 205,
                    "data": f"【Error】zxingcpp 结果解析失败。\n[Error] zxingcpp resule to dict failed.\n {e}",
                }

        res = _run()
        if imgPath:
            res["fileName"] = os.path.basename(imgPath)
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


"""
zxingcpp 返回值类型
# 字节
bytes <class 'bytes'>: b'testtesttesttest'
# 内容类型
content_type <class 'zxingcpp.ContentType'>: ContentType.Text
    name <class 'str'>: Text
    value <class 'int'>: 0
    Binary <class 'zxingcpp.ContentType'>: ContentType.Binary
    GS1 <class 'zxingcpp.ContentType'>: ContentType.GS1
    ISO15434 <class 'zxingcpp.ContentType'>: ContentType.ISO15434
    Mixed <class 'zxingcpp.ContentType'>: ContentType.Mixed
    Text <class 'zxingcpp.ContentType'>: ContentType.Text
    UnknownECI <class 'zxingcpp.ContentType'>: ContentType.UnknownECI
ec_level <class 'str'>: M
# 二维码格式
format <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.QRCode
    name <class 'str'>: QRCode
    value <class 'int'>: 8192
    Aztec <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.Aztec
    Codabar <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.Codabar
    Code128 <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.Code128
    Code39 <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.Code39
    Code93 <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.Code93
    DataBar <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.DataBar
    DataBarExpanded <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.DataBarExpanded
    DataMatrix <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.DataMatrix      
    EAN13 <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.EAN13
    EAN8 <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.EAN8
    ITF <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.ITF
    LinearCodes <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.LinearCodes    
    MatrixCodes <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.MatrixCodes    
    MaxiCode <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.MaxiCode
    MicroQRCode <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.MicroQRCode    
    NONE <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.NONE
    PDF417 <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.PDF417
    QRCode <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.QRCode
    UPCA <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.UPCA
    UPCE <class 'zxingcpp.BarcodeFormat'>: BarcodeFormat.UPCE
# 方向
orientation <class 'int'>: 0
# 位置
position <class 'zxingcpp.Position'>: 16x16 116x16 116x116 16x116
    bottom_left <class 'zxingcpp.Point'>: <zxingcpp.Point object at 0x00000222AEE5C370>
    bottom_right <class 'zxingcpp.Point'>: <zxingcpp.Point object at 0x00000222C19D07B0>
    top_left <class 'zxingcpp.Point'>: <zxingcpp.Point object at 0x00000222AEE5C370>
    top_right <class 'zxingcpp.Point'>: <zxingcpp.Point object at 0x00000222C19D0770>
symbology_identifier <class 'str'>: ]Q1
text <class 'str'>: testtesttesttest
valid <class 'bool'>: True


            def print_all_attributes(obj, layer=0):
                nonlocal last
                for attr_name in dir(obj):
                    if attr_name.startswith("__"):
                        continue
                    attr_value = getattr(obj, attr_name)
                    if callable(attr_value):
                        continue
                    print(
                        "   " * layer, f"{attr_name} {type(attr_value)}: {attr_value}"
                    )
                    last = attr_name
                    l = ["content_type", "format", "position"]
                    if attr_name in l:
                        print_all_attributes(attr_value, layer + 1)
"""
