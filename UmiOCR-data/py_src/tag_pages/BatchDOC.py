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
    # docs为列表，每一项为： {path:文档路径, range_start:范围起始, range_end: 范围结束}
    # 返回一个列表，每项为： {path:文档路径, msnID:任务ID。若[Error]开头则为失败。}
    def msnDocs(self, docs, argd):
        if self._msnIdPath:
            return "[Error] 有任务进行中，不允许提交新任务。"
        resList = []
        for d in docs:
            msnInfo = {
                "onStart": self._onStart,
                "onReady": self._onReady,
                "onGet": self._onGet,
                "onEnd": self._onEnd,
                "argd": argd,
            }
            path = d["path"]
            pageRange = [int(d["range_start"]), int(d["range_end"])]
            msnID = MissionDOC.addMission(msnInfo, path, pageRange)
            if not msnID.startswith("["):  # 添加任务成果才记录到 _msnIdPath
                self._msnIdPath[msnID] = path
            res = {"path": path, "msnID": msnID}
            resList.append(res)
        return resList

    # ========================= 【任务控制器的异步回调】 =========================

    def _onStart(self, msnInfo):  # 任务队列开始
        print(f'=== 开始：{msnInfo["path"]}')

    def _onReady(self, msnInfo, page):  # 单个任务准备
        pass
        # print(f'准备：{msnInfo["path"][-10:]} {page}')

    def _onGet(self, msnInfo, page, res):  # 单个任务完成
        pass
        print(f'获取：{msnInfo["path"][-10:]} {page}')

    def _onEnd(self, msnInfo, page):  # 任务队列完成或失败
        # msg: [Success] [Warning] [Error]
        pass
        print(f'=== 结束：{msnInfo["path"]}')
