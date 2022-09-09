import time
from operator import eq
from config import Config
from ocrAPI import OcrAPI

# TODO：目前这个类是线程不安全的，也是我想把OCR子线程常驻后台的阻碍


class OcrEngine:
    """OCR引擎，含各种操作的方法"""

    def __initVar(self):
        self.ocr = None  # OCR API对象
        self.ocrInfo = ()  # OCR参数

    def __init__(self):
        self.__initVar()

    def __del__(self):
        self.stop()

    def start(self):
        """启动引擎。若引擎已启动，且参数有更新，则重启。"""
        def updateOcrInfo():  # 更新OCR参数。若有更新(与当前不同)，返回True
            info = (
                Config.get("ocrToolPath"),  # 识别器路径
                Config.get("ocrConfig")[Config.get(
                    "ocrConfigName")]['path'],  # 配置文件路径
                Config.get("argsStr"),  # 启动参数
            )
            isUpdate = not eq(info, self.ocrInfo)
            if isUpdate:
                self.ocrInfo = info
            return isUpdate
        isUpdate = updateOcrInfo()
        if self.ocr:  # 已启动
            if not isUpdate:  # 无更新则放假
                return
            self.stop()  # 有更新则先停止OCR进程再启动
        try:
            self.ocr = OcrAPI(*self.ocrInfo)  # 启动引擎
        except Exception as e:
            print(f'OCR进程启动失败：{e}')
            self.stop()
            raise

    def stop(self):
        """立刻终止引擎"""
        del self.ocr  # 关闭OCR进程
        self.__initVar()

    def run(self, path):
        if not self.ocr:
            return {'code': 404, 'data': f'引擎未在运行'}
        return self.ocr.run(path)


OCRe = OcrEngine()  # 引擎单例
