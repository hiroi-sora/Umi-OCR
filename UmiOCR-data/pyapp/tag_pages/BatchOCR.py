# ========================================
# =============== 批量OCR页 ===============
# ========================================

import os
from .page import Page

# from ..ocr.mission_controller import Mission
from ..mission.mission_ocr import MissionOCR

from PySide2.QtCore import Slot

import threading  # TODO: 测试


class BatchOCR(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.msnID = ""

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

    def msnPaths(self, paths, pageDict):  # 接收路径列表和配置，开始OCR任务
        # 初解析配置字典，提取OCR参数
        # 获取qml配置字典
        print("获取配置字典：", pageDict)
        # return
        # 任务信息
        msnInfo = {
            "onStart": self.__onStart,
            "onReady": self.__onReady,
            "onGet": self.__onGet,
            "onFinish": self.__onFinish,
            "onFailure": self.__onFinish,
        }
        self.msnID = MissionOCR.addMissionList(msnInfo, paths)
        if self.msnID:
            print(
                f"在线程{threading.current_thread().ident}添加{len(paths)}个任务，id为{self.msnID}"
            )
            self.callQml("setMsnState", "run")
        else:
            print(f"添加任务失败")
            self.callQml("setMsnState", "None")

    def msnStop(self):  # 任务停止（同步）
        leftover = MissionOCR.stopMissionList(self.msnID)
        return leftover

    # ========================= 【任务控制器的异步回调】 =========================

    def __onStart(self, msnInfo):  # 任务队列开始
        pass

    def __onReady(self, msnInfo, path):  # 单个任务准备
        self.callQmlInMain("onOcrReady", path)

    def __onGet(self, msnInfo, path, res):  # 单个任务完成
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
        self.callQmlInMain("onOcrGet", path, res)  # 在主线程中调用qml

    def __onFinish(self, msnInfo):  # 任务队列完成或失败
        self.callQmlInMain("onOcrFinish")

    # 设置任务状态
    def __setMsnState(self, flag):
        print(f"在线程{threading.current_thread().ident}设置工作状态{flag}")
        self.callQmlInMain("setMsnState", flag)
