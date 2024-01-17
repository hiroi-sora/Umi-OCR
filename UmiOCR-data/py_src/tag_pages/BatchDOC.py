# ========================================
# =============== 批量PDF页 ===============
# ========================================

from .page import Page  # 页基类

from ..mission.mission_doc import MissionDOC  # 任务管理器
from ..utils import utils


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
        # 组装参数字典
        docArgd = {"tbpu.ignoreArea": argd["tbpu.ignoreArea"]}
        for k in argd:
            if k.startswith("ocr.") or k.startswith("doc."):
                docArgd[k] = argd[k]
        print("文档参数：", docArgd)
        # 对每个文档发起一个任务
        for d in docs:
            msnInfo = {
                "onStart": self._onStart,
                "onReady": self._onReady,
                "onGet": self._onGet,
                "onEnd": self._onEnd,
                "argd": docArgd,
            }
            path = d["path"]
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
        self.callQmlInMain("onDocEnd", msnInfo["path"], msg)
