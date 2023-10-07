# ===========================================
# =============== OCR 调用接口 ===============
# ===========================================

from .api_paddleocr import ApiPaddleOcr
from .api_rapidocr import ApiRapidOcr
from .api_ocr import ApiOcr

# 控制器类字典，键与OcrManager.qml中一致
ApiDict = {"PaddleOCR": ApiPaddleOcr, "RapidOCR": ApiRapidOcr}


# 判断一个值是否为OCR对象
def isApiOcr(a):
    return isinstance(a, ApiOcr)


# 生成一个ocr api实例，成功返回对象，失败返回 [Error] 开头的字符串
def getApiOcr(apiKey, argd):
    if apiKey in ApiDict:
        try:
            return ApiDict[apiKey](argd)  # 实例化后返回
        except Exception as e:
            print("!!报错：", e)
            return str(e)
    return f'[Error] "{apiKey}" not in ApiDict.'
