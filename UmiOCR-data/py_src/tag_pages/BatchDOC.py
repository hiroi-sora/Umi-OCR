# ========================================
# =============== 批量文档页 ===============
# ========================================

from .page import Page  # 页基类
from ..mission.mission_doc import MissionDOC  # 任务管理器
from ..utils import utils
from ..ocr.output import Output
from ..ocr.tbpu import Merge as tbpuMerge

import os
import time


class BatchDOC(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self._msnIdPath = {}  # 当前运行的任务，id到地址的映射

    # 添加一些文档
    def addDocs(self, paths, isRecurrence):
        paths = utils.findDocs(paths, isRecurrence)
        docs = []
        for p in paths:
            info = MissionDOC.getDocInfo(p)
            if "error" in info:
                print(f'[Warning] 读入文档失败：{p}\n{info["error"]}')
                continue
            docs.append(info)
        # 返回：{ "path" , "page_count" }
        return docs

    # 进行任务。
    # docs为列表，每一项为： {path:文档路径, range_start:范围起始, range_end: 范围结束, password:密码}
    # 返回一个列表，每项为： {path:文档路径, msnID:任务ID。若[Error]开头则为失败。}
    def msnDocs(self, docs, argd):
        if self._msnIdPath:
            return "[Error] 有任务进行中，不允许提交新任务。"
        resList = []
        # 组装参数字典。tbpu分两部分，在MissionDOC中执行ignoreArea，本文件执行merge
        docArgd = {"tbpu.ignoreArea": argd["tbpu.ignoreArea"]}
        for k in argd:
            if k.startswith("ocr.") or k.startswith("doc."):
                docArgd[k] = argd[k]
        # 段落合并
        tbpuList = []
        if "tbpu.merge" in argd and argd["tbpu.merge"] != "None":
            if argd["tbpu.merge"] in tbpuMerge:
                tbpuList.append(tbpuMerge[argd["tbpu.merge"]]())
            else:
                print(f'[Error] 段落合并参数不存在： {argd["tbpu.merge"]}')
        # 对每个文档发起一个任务
        for d in docs:
            path = d["path"]
            # 构造输出器，output1为PDF型输出器，output2为普通文本型输出器。
            output1, output2 = self._initOutputList(argd, path)
            if type(output1) == str:  # 创建输出器失败
                resList.append({"path": path, "msnID": output1})
                continue
            # 任务信息
            msnInfo = {
                "onStart": self._onStart,
                "onReady": self._onReady,
                "onGet": self._onGet,
                "onEnd": self._onEnd,
                "argd": docArgd,
                # 交给 self._onGet 的参数
                "get_output1": output1,
                "get_output2": output2,
                "get_tbpu": tbpuList,
            }
            pageRange = [int(d["range_start"]), int(d["range_end"])]
            password = d["password"]
            msnID = MissionDOC.addMission(msnInfo, path, pageRange, password=password)
            if not msnID.startswith("["):  # 添加任务成果才记录到 _msnIdPath
                self._msnIdPath[msnID] = path
            res = {"path": path, "msnID": msnID}
            resList.append(res)
        return resList

    # 停止当前所有任务
    def msnStop(self):
        for msnID in self._msnIdPath:
            MissionDOC.stopMissionList(msnID)
        self._msnIdPath = {}

    # 初始化输出器列表。成功返回两个输出器列表 output1, output2 。失败返回 "失败信息", None
    def _initOutputList(self, argd, path):
        # =============== 提取输出路径 outputDir, outputDirName ===============
        if argd["mission.dirType"] == "source":  # 若保存到原目录
            outputDir = os.path.dirname(path)  # 则保存路径设为文档的目录
        else:  # 若保存到用户指定目录
            d = os.path.abspath(argd["mission.dir"])  # 转绝对地址
            if not os.path.exists(d):  # 检查地址是否存在
                try:  # 不存在，尝试创建地址
                    os.makedirs(d)
                except OSError as e:
                    return f"[Error] 无法创建路径 {d}", None
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
        # 处理文件名
        nameTemplate = argd["mission.fileNameFormat"]
        nameTemplate = nameTemplate.replace(r"%date", startDatetimeUser)  # 替换时间
        fileNameEle = os.path.splitext(os.path.basename(path))[0]
        outputFileName = nameTemplate.replace("%name", fileNameEle)  # 替换名称元素
        if not utils.allowedFileName(outputFileName):  # 文件名不合法
            return (
                f'[Error] 文件名【{outputFileName}】含有不允许的字符。\n不允许含有下列字符： \  /  :  *  ?  "  <  >  |',
                None,
            )

        # =============== 组装输出参数字典 ===============
        outputArgd = {
            "outputDir": outputDir,  # 输出路径
            "outputDirType": argd["mission.dirType"],  # 输出目录类型，"source" 为原文件目录
            "outputFileName": outputFileName,  # 输出文件名（前缀）
            "startDatetime": startDatetime,  # 开始日期
            "ingoreBlank": argd["mission.ingoreBlank"],  # 忽略空白文件
            "originPath": path,  # 原始文件名
        }

        # =============== 实例化输出器对象 ===============
        output1, output2 = [], []
        try:
            for key in argd.keys():
                # 列表1，输出为PDF格式，需要在tbpu之前输出
                if "mission.filesType.pdf" in key and argd[key]:
                    output1.append(Output[key[18:]](outputArgd))
                # 列表2，输出为文本格式，在tbpu之后输出
                elif "mission.filesType" in key and argd[key]:
                    output2.append(Output[key[18:]](outputArgd))
        except Exception as e:
            return (f"[Error] 初始化输出器失败。{e}", None)
        return output1, output2

    # ========================= 【任务控制器的异步回调】 =========================

    def _onStart(self, msnInfo):  # 一个文档 开始
        msnID = msnInfo["msnID"]
        if msnID not in self._msnIdPath:
            print(f"[Warning] _onStart 任务ID未在记录。{msnID}")
            return
        self.callQmlInMain("onDocStart", msnInfo["path"])

    def _onReady(self, msnInfo, page):  # 一个文档的一页 准备开始
        page += 1
        pass

    def _onGet(self, msnInfo, page, res):  # 一个文档的一页 获取结果
        page += 1
        msnID = msnInfo["msnID"]
        if msnID not in self._msnIdPath:
            print(f"[Warning] _onGet 任务ID未在记录。{msnID}")
            return

        def runOutput(output):
            for o in output:
                try:
                    o.print(res)
                except Exception as e:
                    print(f"文档结果输出失败：{o}\n{e}")

        # 提取信息
        output1, output2 = msnInfo["get_output1"], msnInfo["get_output2"]
        tbpuList = msnInfo["get_tbpu"]

        # 为 res 添加信息
        res["page"] = page
        res["fileName"] = f"{page}"
        res["path"] = msnInfo["path"]

        runOutput(output1)  # 输出第1部分
        if tbpuList and res["code"] == 100:  # 执行tbpu
            size = {"w": msnInfo["pageInfo"]["w"], "h": msnInfo["pageInfo"]["h"]}
            data = res["data"]
            for tbpu in tbpuList:
                data = tbpu.run(data, size)
            res["data"] = data
        runOutput(output2)  # 输出第2部分

        self.callQmlInMain("onDocGet", msnInfo["path"], page, res)

    def _onEnd(self, msnInfo, msg):  # 一个文档处理完毕
        # msg: [Success] [Warning] [Error]
        msnID = msnInfo["msnID"]
        if msnID not in self._msnIdPath:
            print(f"[Warning] _onEnd 任务ID未在记录。{msnID}")
            return
        del self._msnIdPath[msnID]

        if not self._msnIdPath:  # 全部完成
            msg = "[Success] All completed."
        # 结束输出器，保存文件。
        output1, output2 = msnInfo["get_output1"], msnInfo["get_output2"]
        for outputs in (output1, output2):
            for o in outputs:
                try:
                    o.onEnd()
                except Exception as e:
                    msg = f"[Error] 输出器异常：{e}" + msg
        self.callQmlInMain("onDocEnd", msnInfo["path"], msg)
