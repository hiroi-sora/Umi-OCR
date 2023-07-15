# ===========================================
# =============== OCR 调用接口 ===============
# ===========================================

from .api_paddleocr import ApiPaddleOCR


def getOcrApi():  # 返回一个ocr api实例
    return ApiPaddleOCR()
