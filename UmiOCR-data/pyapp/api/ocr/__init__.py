# ===========================================
# =============== OCR 调用接口 ===============
# ===========================================

from .api_paddleocr import ApiPaddleOcr

# 控制器类字典，键与OcrManager.qml中一致
ApiDict = {"PaddleOCR": ApiPaddleOcr}


def getApiOcr(apiKey):  # 返回一个ocr api实例
    if apiKey in ApiDict:
        return ApiDict[apiKey]()  # 实例化后返回
    return None
