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
