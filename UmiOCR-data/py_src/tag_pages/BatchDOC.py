# ========================================
# =============== 批量文档页 ===============
# ========================================

from .page import Page  # 页基类
from ..mission.mission_doc import MissionDOC  # 任务管理器
from ..utils import utils
from ..ocr.output import Output
from ..ocr.tbpu import getParser
from ..utils.thread_pool import threadRun  # 异步执行函数

import os
import time


class BatchDOC(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self._msnID = ""  # 当前正在进行的任务ID（已提交至任务处理器）
        self._pauseMsnID = ""  # 当前正在暂停的任务ID
        self._queuedDocs = []  # 当前正在排队的文档信息（未提交）
        self._argd = None
        self._docArgd = None

    # 添加一些文档
    def addDocs(self, paths, isRecurrence):
        threadRun(self._addDocsThread, paths, isRecurrence)

    # 添加一些文档
    def _addDocsThread(self, paths, isRecurrence):
        paths = utils.findDocs(paths, isRecurrence)
        docs = []
        for p in paths:
            info = MissionDOC.getDocInfo(p)
            if "error" in info:
                print(f'[Warning] 读入文档失败：{p}\n{info["error"]}')
                continue
            docs.append(info)
        # 回调传入：{ "path" , "page_count" }
        self.callQmlInMain("onAddDocs", docs)

    # 进行任务。
    # docs为列表，每一项为： {path:文档路径, range_start:范围起始, range_end: 范围结束, page_count:总页数, password:密码}
    # 返回一个列表，每项为： {path:文档路径, msnID:任务ID。若[Error]开头则为失败。}
    def msnDocs(self, docs, argd):
        if self._msnID or self._queuedDocs:
            return "[Error] 有任务进行中，不允许提交新任务。"

        # 从 argd 中提取一些条目，组装 docArgd
        prefixes = ["ocr.", "doc.", "tbpu."]  # 要提取的条目前缀
        docArgd = {}
        for k, v in argd.items():
            for prefix in prefixes:
                if k.startswith(prefix):
                    docArgd[k] = v
                    break

        # 记录任务参数
        self._queuedDocs = docs
        self._argd = argd
        self._docArgd = docArgd
        # 提交第一个任务
        self._runNewDoc()

    def msnStop(self):  # 停止当前所有任务
        MissionDOC.stopMissionList(self._msnID)
        self._msnID = ""
        self._queuedDocs = []
        self._argd = None
        self._docArgd = None

    def msnPause(self):  # 任务暂停
        self._pauseMsnID = self._msnID
        MissionDOC.pauseMissionList(self._msnID)

    def msnResume(self):  # 任务恢复
        self._pauseMsnID = ""
        MissionDOC.resumeMissionList(self._msnID)

    # 初始化输出器列表。成功返回两个输出器列表 output 。失败返回 "失败信息"
    def _initOutputList(self, argd, path, pageRange, pageCount, password=""):
        # =============== 提取输出路径 outputDir, outputDirName ===============
        if argd["mission.dirType"] == "source":  # 若保存到原目录
            outputDir = os.path.dirname(path)  # 则保存路径设为文档的目录
        else:  # 若保存到用户指定目录
            d = os.path.abspath(argd["mission.dir"])  # 转绝对地址
            if not os.path.exists(d):  # 检查地址是否存在
                try:  # 不存在，尝试创建地址
                    os.makedirs(d)
                except OSError as e:
                    return f"[Error] 无法创建路径 {d}"
            outputDir = d

        # =============== 提取时间信息和文件名 outputFileName ===============
        startTimestamp = time.time()  # 开始时间戳
        startDatetime = time.strftime(  # 日期时间字符串（标准格式）
            r"%Y-%m-%d %H:%M:%S", time.localtime(startTimestamp)
        )
        # 日期时间字符串（用户指定格式）：先替换时间戳，再strftime
        startDatetimeUser = argd["mission.datetimeFormat"].replace(
            r"%unix", str(startTimestamp)
        )
        startDatetimeUser = time.strftime(
            startDatetimeUser, time.localtime(startTimestamp)
        )
        # 替换时间 %date
        nameTemplate = argd["mission.fileNameFormat"]
        nameTemplate = nameTemplate.replace(r"%date", startDatetimeUser)  # 替换时间
        # 替换范围 %range
        rangeStr = ""  # 范围全本
        if pageRange[1] - pageRange[0] + 1 < pageCount:  # 范围非全本
            if pageRange[1] == pageRange[0]:  # 只识别一页，写入单个页数
                rangeStr = f"(p{pageRange[0]})"
            else:  # 识别多页，写入开头和结尾页数
                rangeStr = f"(p{pageRange[0]}-{pageRange[1]})"
        nameTemplate = nameTemplate.replace(r"%range", rangeStr)
        # 替换文件名 #name
        fileNameStr = os.path.splitext(os.path.basename(path))[0]
        outputFileName = nameTemplate.replace(r"%name", fileNameStr)  # 替换名称元素
        if not utils.allowedFileName(outputFileName):  # 文件名不合法
            return f'[Error] 文件名【{outputFileName}】含有不允许的字符。\n不允许含有下列字符： \  /  :  *  ?  "  <  >  |'

        # =============== 组装输出参数字典 ===============
        outputArgd = {
            "outputDir": outputDir,  # 输出路径
            "outputDirType": argd[
                "mission.dirType"
            ],  # 输出目录类型，"source" 为原文件目录
            "outputFileName": outputFileName,  # 输出文件名（前缀）
            "startDatetime": startDatetime,  # 开始日期
            "ingoreBlank": argd["mission.ingoreBlank"],  # 忽略空白文件
            "originPath": path,  # 原始文件名
            "password": password,  # 文档密码
        }

        # =============== 实例化输出器对象 ===============
        output = []
        try:
            for key in argd.keys():
                if "mission.filesType" in key and argd[key]:
                    output.append(Output[key[18:]](outputArgd))
        except Exception as e:
            return f"[Error] 初始化输出器失败。{e}"
        return output

    def _runNewDoc(self):  # 取 self._queuedList 首位任务，提交执行
        if not self._queuedDocs:
            print("[Warning] 文档任务： queuedDocs 已空")
            return
        d = self._queuedDocs.pop(0)  # 取首位任务
        path = d["path"]  # 取地址
        password = d["password"]  # 密码
        pageRange = [int(d["range_start"]), int(d["range_end"])]  # 识别范围
        pageCount = int(d["page_count"])  # 总页数
        # 构造输出器
        output = self._initOutputList(self._argd, path, pageRange, pageCount, password)
        if type(output) == str:  # 创建输出器失败
            self._onEnd({"path": path}, "[Error] 无法创建输出器。")
            return
        # 任务信息
        msnInfo = {
            "onStart": self._onStart,
            "onReady": self._onReady,
            "onGet": self._onGet,
            "onEnd": self._onEnd,
            "argd": self._docArgd,
            # 交给 self._onGet 的参数
            "get_output": output,
        }
        msnID = MissionDOC.addMission(msnInfo, path, pageRange, password=password)
        if msnID.startswith("["):  # 添加任务失败
            self._msnID = ""
            self._onEnd({"path": path}, msnID)
        else:
            self._msnID = msnID

    # ========================= 【任务控制器的异步回调】 =========================

    def _onStart(self, msnInfo):  # 一个文档 开始
        msnID = msnInfo["msnID"]
        if not msnID == self._msnID:
            print(f"[Warning] _onStart 任务ID未在记录。{msnID}")
            return
        self.callQmlInMain("onDocStart", msnInfo["path"])

    def _onReady(self, msnInfo, page):  # 一个文档的一页 准备开始
        page += 1

    def _onGet(self, msnInfo, page, res):  # 一个文档的一页 获取结果
        page += 1
        msnID = msnInfo["msnID"]
        if not msnID == self._msnID:
            print(f"[Warning] _onGet 任务ID未在记录。{msnID}")
            return

        # 为 res 添加信息
        res["page"] = page
        res["fileName"] = f"{page}"
        res["path"] = msnInfo["path"]

        # 输出
        for o in msnInfo["get_output"]:
            try:
                o.print(res)
            except Exception as e:
                print(f"文档结果输出失败：{o}\n{e}")

        self.callQmlInMain("onDocGet", msnInfo["path"], page, res)

    def _onEnd(self, msnInfo, msg):  # 一个文档处理完毕
        # msg: [Success] [Warning] [Error]

        if "path" not in msnInfo:
            raise Exception('[Error] BatchDOC onEnd(): "path" not in msnInfo')

        msnID = ""  # 该任务的ID
        if "msnID" in msnInfo:
            msnID = msnInfo["msnID"]
            if not msnID == self._msnID:
                print(f"[Warning] _onEnd 任务ID未在记录。{msnID}")
                return

        # 结束输出器，保存文件。
        if "get_output" in msnInfo:
            output = msnInfo["get_output"]
            for o in output:
                try:
                    o.onEnd()
                except Exception as e:
                    msg = f"[Error] 输出器异常：{e}" + msg

        # 上报
        isAll = False if self._queuedDocs else True  # 是否所有文档处理完毕
        self.callQmlInMain("onDocEnd", msnInfo["path"], msg, isAll)

        # 所有任务完毕
        if isAll:
            self._msnID = ""
            self._argd = None
            self._docArgd = None
        # 还有排队中的任务，则提交新任务
        else:
            self._runNewDoc()
            # 如果新任务 self._msnID 已提交成功，且上一个任务 msnID 处于暂停状态，
            # 也就是在保存文件的过程中，用户点了暂停，
            # 那么将新的任务设为暂停。
            if self._msnID and msnID and self._pauseMsnID == msnID:
                self.msnPause()
