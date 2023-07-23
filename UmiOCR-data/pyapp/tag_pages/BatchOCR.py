# ========================================
# =============== 批量OCR页 ===============
# ========================================

from .page import Page
from ..mission.mission_ocr import MissionOCR
from ..utils.utils import allowedFileName

# 输出器
from ..ocr.output.output_txt import OutputTxt

import os
import json
import time
from PySide2.QtCore import Slot
import threading  # TODO: 测试


class BatchOCR(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.msnID = ""
        self.outputList = []  # 输出器列表

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

    def msnPaths(self, paths, argd):  # 接收路径列表和配置，开始OCR任务
        # 任务信息
        msnInfo = {
            "onStart": self.__onStart,
            "onReady": self.__onReady,
            "onGet": self.__onGet,
            "onEnd": self.__onEnd,
            "argd": argd,
        }
        # 初步处理参数
        startTimestamp = time.time()  # 开始时间戳
        argd["startTimestamp"] = startTimestamp
        argd["startDatetime"] = time.strftime(  # 格式化日期时间
            "%Y-%m-%d %H:%M:%S", time.localtime(startTimestamp)
        )
        if argd["mission.dirType"] == "source":  # 若保存到原目录
            argd["mission.dir"] = os.path.dirname(paths[0])  # 则保存路径设为第1张图片的目录
        fileName = argd["mission.fileName"]
        if not allowedFileName(fileName):  # 文件名不合法
            self.__onEnd(
                None,
                '[Error] The file name is illegal.\n【错误】文件名【{fileName}】含有不允许的字符。\n不允许含有下列字符： \  /  :  *  ?  "  <  >  |',
            )
            return
        # 构造输出器
        self.__initOutputList(argd)
        # 路径转为任务列表格式，加载进任务管理器
        msnList = [{"path": x} for x in paths]
        self.msnID = MissionOCR.addMissionList(msnInfo, msnList)
        if self.msnID:  # 添加成功，通知前端刷新UI
            self.callQml("setMsnState", "run")
        else:  # 添加任务失败
            self.__onEnd(None, "[Error] Failed to add task.\n【错误】添加任务失败。")

    def __initOutputList(self, argd):  # 初始化输出器列表
        fileName = argd["mission.fileName"]
        self.outputList = []
        try:
            if argd["mission.filesType.txt"]:  # 标准txt
                self.outputList.append(
                    OutputTxt(argd["mission.dir"], fileName, argd["startDatetime"])
                )
        except Exception as e:
            self.__onEnd(
                None,
                f"[Error] Failed to initialize output file.\n【错误】初始化输出文件失败。\n{e}",
            )
            return

    def msnStop(self):  # 任务停止（异步）
        MissionOCR.stopMissionList(self.msnID)

    # ========================= 【任务控制器的异步回调】 =========================

    def __onStart(self, msnInfo):  # 任务队列开始
        pass

    def __onReady(self, msnInfo, msn):  # 单个任务准备
        self.callQmlInMain("onOcrReady", msn["path"])

    def __onGet(self, msnInfo, msn, res):  # 单个任务完成
        # 计算平均置信度
        score = 0
        num = 0
        if res["code"] == 100:
            for r in res["data"]:
                score += r["score"]
                num += 1
            if num > 0:
                score /= num
        # 补充参数
        res["score"] = score
        res["path"] = msn["path"]
        res["fileName"] = os.path.basename(msn["path"])
        res["dir"] = os.path.dirname(msn["path"])
        # 输出器输出
        for o in self.outputList:
            o.print(res)
        # 通知qml更新UI
        self.callQmlInMain("onOcrGet", msn["path"], res)  # 在主线程中调用qml

    def __onEnd(self, msnInfo, msg):  # 任务队列完成或失败
        # msg: [Success] [Warning] [Error]
        self.callQmlInMain("onOcrEnd", msg)
        # TODO: debug 打开文件
        for o in self.outputList:
            o.openOutputFile()

    # 设置任务状态
    def __setMsnState(self, flag):
        print(f"在线程{threading.current_thread().ident}设置工作状态{flag}")
        self.callQmlInMain("setMsnState", flag)
