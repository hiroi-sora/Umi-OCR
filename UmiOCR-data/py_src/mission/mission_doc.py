# ===============================================
# =============== 文档 - 任务管理器 ===============
# ===============================================

from .mission import Mission
from .mission_ocr import MissionOCR

import fitz  # PyMuPDF


class _MissionDocClass(Mission):
    # msnInfo: { 回调函数"onXX", 参数"argd":{"tbpu.xx", "ocr.xx"} }
    # msnFile: { 可选 "path", "bytes", "base64" }
    # pageRange 可选：
    # None - 整本
    # int - 单页
    # (1,3) - 页面范围
    # [1,2,4,5] - 多个页面
    def addMissionList(self, msnInfo, msnFile, pageRange=None):
        if "path" in msnFile:
            doc = fitz.open(msnFile["path"])
        else:
            raise Exception("暂不支持 bytes base64 传入PDF")
        msnInfo["doc"] = doc
        msnList = list(range(doc.page_count))
        return super().addMissionList(msnInfo, msnList)

    def msnTask(self, msnInfo, pno):  # 执行msn
        doc = msnInfo["doc"]
        page = doc[pno]
        # 获取元素
        p = page.get_text("dict")
        imgs = []
        print(f"= 页 {pno}")
        for t in p["blocks"]:
            if t["type"] == 1:  # 图片
                imgs.append({"bytes": t["image"]})
        argd = msnInfo["argd"]
        resList = MissionOCR.addMissionWait(argd, imgs)
        print(f"# {pno}")
        for res in resList:
            print(res["result"])
        return None


# 全局 DOC 任务管理器
MissionDOC = _MissionDocClass()
