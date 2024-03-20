# =================================================
# =============== 二维码 - 任务管理器 ===============
# =================================================

import base64
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from .mission import Mission

try:
    import zxingcpp
except Exception as e:
    zxingcpp = None
    zxingcppErr = str(e)


class _MissionQRCodeClass(Mission):

    def createImage(self, text, format="QRCode", w=0, h=0, quiet_zone=-1, ec_level=-1):
        """
        生成二维码图片
        format: "Aztec","Codabar","Code128","Code39","Code93","DataBar","DataBarExpanded","DataMatrix","EAN13","EAN8","ITF","LinearCodes","MatrixCodes","MaxiCode","MicroQRCode","PDF417","QRCode","UPCA","UPCE",
        quiet_zone: 四周的空闲区域
        ec_level：纠错等级，-1 - 自动, 1- L-7% , 0 - M-15%, 3 - Q-25%, 2 - H-30%
        纠错仅用于Aztec、PDF417和QRCode
        返回：成功返回PIL对象，失败返回错误原因字符串
        """
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
        return img

    # msnInfo: { 回调函数"onXX" , 参数"argd":{ "preprocessing.xx" } }
    # msnList: [ { "path", "pil", "base64" } ]
    # def addMissionList(self, msnInfo, msnList):  # 添加任务列表
    #     return super().addMissionList(msnInfo, msnList)
    def msnTask(self, msnInfo, msn):  # 执行msn
        # 导入库失败
        if not zxingcpp:
            return {
                "code": 901,
                "data": f"【Error】无法导入二维码解析器 zxingcpp 。\n[Error] Unable to import zxingcpp.\n{zxingcppErr}",
            }
        # 读入图片
        try:
            if "pil" in msn:
                img = msn["pil"]
            elif "path" in msn:
                imgPath = msn["path"]
                img = Image.open(imgPath)
            elif "base64" in msn:
                imgBase64 = msn["base64"]
                img = Image.open(BytesIO(base64.b64decode(imgBase64)))
        except Exception as e:
            return {
                "code": 202,
                "data": f"【Error】图片读取失败。\n[Error] Image reading failed.\n {e}",
            }
        # 预处理
        if "argd" in msnInfo:
            try:
                img = self._preprocessing(img, msnInfo["argd"])
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

    # 图像预处理
    def _preprocessing(self, img, argd):
        """
        对图像进行预处理，包括中值滤波、锐度增强、对比度增强以及可选的灰度转换和二值化。

        img: PIL.Image对象，待处理的图像。
        argd: 参数字典，包含以下可选键值对：
            - "preprocessing.median_filter_size": 中值滤波器的大小，应为1~9的奇数。默认不进行。
            - "preprocessing.sharpness_factor": 锐度增强因子，应为0.1~10。默认不调整锐度。
            - "preprocessing.contrast_factor": 对比度增强因子，应为0.1~10。大于1增强对比度，小于1但大于0减少对比度，1保持原样。默认不调整对比度。
            - "preprocessing.grayscale": 布尔值，指定是否将图像转换为灰度图像。True为转换，False为不转换。默认为False。
            - "preprocessing.threshold": 二值化阈值，用于灰度图像的二值化处理。应为0到255之间的整数。只有当"preprocessing.grayscale"为True时，此参数才生效。默认不进行二值化处理。

        返回:
        处理后的PIL.Image对象。
        """

        # 中值滤波
        s = round(argd.get("preprocessing.median_filter_size", -100))
        if s > 0 and s % 2 == 1:
            img = img.filter(ImageFilter.MedianFilter(size=s))
        # 锐度增强
        f = round(argd.get("preprocessing.sharpness_factor", -100))
        if f > 0:
            img = ImageEnhance.Sharpness(img).enhance(f)
        # 对比度增强
        c = argd.get("preprocessing.contrast_factor", -100)
        if c > 0:
            img = ImageEnhance.Contrast(img).enhance(c)
        # 转为灰度 & 二值化
        if argd.get("preprocessing.grayscale", False):
            img = img.convert("L")
            t = round(argd.get("preprocessing.threshold", -100))
            if t > -1:
                img = img.point(lambda p: 255 if p > t else 0)
        return img


MissionQRCode = _MissionQRCodeClass()


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
"""
