# ========================================
# =============== 批量OCR页 ===============
# ========================================

from .page import Page  # 页基类
from ..mission.mission_ocr import MissionOCR  # 任务管理器
from ..utils.utils import allowedFileName, findImages as findImages_
from ..platform import Platform  # 跨平台

# 输出器
from ..ocr.output.output_txt import OutputTxt
from ..ocr.output.output_txt_plain import OutputTxtPlain
from ..ocr.output.output_txt_individual import OutputTxtIndividual
from ..ocr.output.output_md import OutputMD
from ..ocr.output.output_jsonl import OutputJsonl

import os
import time
from PySide2.QtCore import Slot


class BatchOCR(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.argd = None
        self.msnID = ""
        self.outputList = []  # 输出器列表

    # ========================= 【qml调用python】 =========================

    def findImages(self, paths, isRecurrence):  # 接收路径列表，在路径中搜索图片。
        return findImages_(paths, isRecurrence)

    def msnPaths(self, paths, argd):  # 接收路径列表和配置参数字典，开始OCR任务
        # 任务信息
        msnInfo = {
            "onStart": self.__onStart,
            "onReady": self.__onReady,
            "onGet": self.__onGet,
            "onEnd": self.__onEnd,
            "argd": argd,
        }
        # 预处理参数字典
        if not self.__preprocessArgd(argd, paths[0]):
            return
        # 构造输出器
        if not self.__initOutputList(argd):
            return
        # 路径转为任务列表格式，加载进任务管理器
        msnList = [{"path": x} for x in paths]
        self.msnID = MissionOCR.addMissionList(msnInfo, msnList)
        if self.msnID:  # 添加成功，通知前端刷新UI
            self.callQml("setMsnState", "run")
            print(f"添加任务成功 {self.msnID}\n{argd}")
        else:  # 添加任务失败
            self.__onEnd(None, "[Error] Failed to add task.\n【错误】添加任务失败。")
        return self.msnID

    def __preprocessArgd(self, argd, path0):  # 预处理参数字典，无异常返回True
        self.argd = None
        if argd["mission.dirType"] == "source":  # 若保存到原目录
            argd["mission.dir"] = os.path.dirname(path0)  # 则保存路径设为第1张图片的目录
        else:  # 若保存到用户指定目录
            d = os.path.abspath(argd["mission.dir"])  # 转绝对地址
            if not os.path.exists(d):  # 检查地址是否存在
                try:  # 不存在，尝试创建地址
                    os.makedirs(d)
                except OSError as e:  # 创建地址失败，报错
                    self.__onEnd(
                        None,
                        f'[Error] Failed to create directory: "{d}"\n【异常】无法创建路径。',
                    )
                    return False
            argd["mission.dir"] = d  # 写回字典
        argd["mission.dirName"] = os.path.basename(argd["mission.dir"])  # 提取最后一层文件夹名称
        print(f'转换\n{argd["mission.dir"]}\n{argd["mission.dirName"]}')
        startTimestamp = time.time()  # 开始时间戳
        argd["startTimestamp"] = startTimestamp
        # 格式化日期时间（标准格式）
        argd["startDatetime"] = time.strftime(
            r"%Y-%m-%d %H:%M:%S", time.localtime(startTimestamp)
        )
        # 添加格式化日期时间（用户指定格式）：先替换时间戳，再strftime
        startDatetimeUser = argd["mission.datetimeFormat"].replace(
            r"%unix", str(startTimestamp)
        )
        startDatetimeUser = time.strftime(
            startDatetimeUser, time.localtime(startTimestamp)
        )
        # 处理文件名
        fileName = argd["mission.fileNameFormat"]
        fileName = fileName.replace(r"%date", startDatetimeUser)  # 替换时间
        if not allowedFileName(fileName):  # 文件名不合法
            self.__onEnd(
                None,
                f'[Error] The file name is illegal.\n【错误】文件名【{fileName}】含有不允许的字符。\n不允许含有下列字符： \  /  :  *  ?  "  <  >  |',
            )
            return False
        argd["mission.fileName"] = fileName  # 回填文件名
        self.argd = argd
        return True

    def __initOutputList(self, argd):  # 初始化输出器列表，无异常返回True
        self.outputList = []
        outputArgd = {  # 数据转换，封装有需要的值
            "outputDir": argd["mission.dir"],  # 输出路径
            "outputDirName": argd["mission.dirName"],  # 输出文件夹名称
            "outputFileName": argd["mission.fileName"],  # 输出文件名（前缀）
            "startDatetime": argd["startDatetime"],  # 开始日期
            "ingoreBlank": argd["mission.ingoreBlank"],  # 忽略空白文件
        }
        try:
            if argd["mission.filesType.txt"]:  # 标准txt
                self.outputList.append(OutputTxt(outputArgd))
            if argd["mission.filesType.txtPlain"]:  # 纯文本txt
                self.outputList.append(OutputTxtPlain(outputArgd))
            if argd["mission.filesType.txtIndividual"]:  # 单独txt
                self.outputList.append(OutputTxtIndividual(outputArgd))
            if argd["mission.filesType.md"]:  # jsonl
                self.outputList.append(OutputMD(outputArgd))
            if argd["mission.filesType.jsonl"]:  # jsonl
                self.outputList.append(OutputJsonl(outputArgd))
        except Exception as e:
            self.__onEnd(
                None,
                f"[Error] Failed to initialize output file.\n【错误】初始化输出文件失败。\n{e}",
            )
            return False
        return True

    def msnStop(self):  # 任务停止（异步）
        MissionOCR.stopMissionList(self.msnID)

    def postTaskActions(self, argd):  # 任务完成后续操作
        # argd可选值 "openFolder": "要打开的目录", "openFile": True(打开上次任务的文件),
        # "shutdown": True(关机), "hibernate": True(休眠)

        # 打开目录
        openFolder = argd.get("openFolder", False)
        if openFolder and os.path.exists(self.argd["mission.dir"]):
            os.startfile(self.argd["mission.dir"])
        # 打开文件
        if argd.get("openFile", False):
            for o in self.outputList:
                o.openOutputFile()
        # 关机
        if argd.get("shutdown", False):
            Platform.shutdown()
        # 休眠
        elif argd.get("hibernate", False):
            Platform.hibernate()

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
            try:
                o.print(res)
            except Exception as e:
                print(f"输出失败：{o}\n{e}")
        # 通知qml更新UI
        self.callQmlInMain("onOcrGet", msn["path"], res)  # 在主线程中调用qml

    def __onEnd(self, msnInfo, msg):  # 任务队列完成或失败
        # msg: [Success] [Warning] [Error]
        self.callQmlInMain("onOcrEnd", msg, self.msnID)
