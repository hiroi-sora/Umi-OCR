# ========================================
# =============== 批量OCR页 ===============
# ========================================

import os
from .page import Page
from ..ocr.mission_controller import Mission

from PySide2.QtCore import Slot

import threading  # TODO: 测试


class BatchOCR(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.mission = Mission(self.__setMsnState)  # 页面自身的任务控制器对象

    # ========================= 【qml调用python】 =========================

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

    def msnPaths(self, paths):  # 接收路径列表，开始OCR任务
        missions = [
            {
                "api": "",
                "args": {"exePath": "./lib/PaddleOCR-json/PaddleOCR-json.exe"},
            }
        ]
        for p in paths:
            missions.append({"path": p, "callback": self.__onGet})
        self.mission.add(missions)  # 添加到OCR任务列表
        print(f"在线程{threading.current_thread().ident}添加{len(missions)}个任务")

    def msnStop(self):  # 任务停止，并清理任务列表
        self.mission.stop()
        self.mission.clear()

    # ========================= 【任务控制器的异步回调】 =========================

    # 单个OCR任务完成
    @Slot("QVariant", "QVariant")
    def __onGet(self, res, msn):
        # print(f"在线程{threading.current_thread().ident}执行回调，返回值\n    {res}")
        # 计算平均置信度
        score = 0
        num = 0
        if res["code"] == 100:
            for r in res["data"]:
                score += r["score"]
                num += 1
            if num > 0:
                score /= num
        res["score"] = score
        self.callQml("setOcrRes", msn["path"], res)

    # 设置任务状态
    @Slot(str)
    def __setMsnState(self, flag):
        print(f"在线程{threading.current_thread().ident}设置工作状态{flag}")
        self.callQml("setMsnState", flag)
