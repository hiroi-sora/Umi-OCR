# ========================================
# =============== 批量OCR页 ===============
# ========================================

import os
from .page import Page
from ..ocr import ocr

from PySide2.QtCore import Slot

import threading  # TODO: 测试


class BatchOCR(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.ocr = None  # 页面自身的OCR模块对象
        self.ocr = ocr.OCR()  # TODO: 测试

    def findImages(self, paths):  # 接收路径列表，在路径中搜索图片
        suf = [
            ".jpg",
            ".jpe",
            ".jpeg",
            ".jfif",
            ".png",
            ".webp",
            ".bmp",
            ".tif",
            ".tiff",
        ]

        def isImg(path):  # 路径是图片返回true
            return os.path.splitext(path)[-1].lower() in suf

        imgPaths = []
        for p in paths:
            if os.path.isfile(p) and isImg(p):  # 是文件，直接判断
                imgPaths.append(os.path.abspath(p))
            elif os.path.isdir(p):  # 是路径
                for root, dirs, files in os.walk(p):
                    for file in files:
                        if isImg(file):  # 收集子文件
                            imgPaths.append(
                                os.path.abspath(os.path.join(root, file))
                            )  # 将路径转换为绝对路径
                    for dir in dirs:  # 继续搜索子目录
                        paths.append(os.path.join(root, dir))
        for i, p in enumerate(imgPaths):  # 规范化正斜杠
            imgPaths[i] = p.replace("\\", "/")
        return imgPaths

    def ocrImages(self, paths):  # 接收路径列表，开始OCR任务
        missions = []
        for p in paths:
            missions.append({"path": p, "callback": self.__ocrCallback})
        self.ocr.add(missions)
        print(f"在线程{threading.current_thread().ident}添加{len(missions)}个任务")

    @Slot("QVariant", "QVariant")
    def __ocrCallback(self, res, msn):  #  单个OCR任务完成的回调，在主线程被调用
        print(f"在线程{threading.current_thread().ident}执行回调，路径{msn['path']}")
