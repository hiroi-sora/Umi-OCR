# ========================================
# =============== 批量PDF页 ===============
# ========================================

from .page import Page  # 页基类

from ..mission.mission_doc import MissionDOC  # 任务管理器
from ..utils import utils


class BatchDOC(Page):
    def __init__(self, *args):
        super().__init__(*args)

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

    def msnDocs(self, docs, argd):
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
            print(f"\n== 任务id {msnID} {path} \n")
            print(argd)
        return ""

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
