# ===============================================
# =============== 文档 - 任务管理器 ===============
# ===============================================

# API所有页数page 均为1开始

from .mission import Mission
from .mission_ocr import MissionOCR

import fitz  # PyMuPDF


class FitzOpen:
    def __init__(self, path):
        self._path = path
        self._doc = None

    def __enter__(self):
        self._doc = fitz.open(self._path)
        return self._doc

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._doc.close()


class _MissionDocClass(Mission):
    def __init__(self):
        super().__init__()
        self._schedulingMode = "1234"  # 调度方式：顺序

    # 添加一个文档任务
    # msnInfo: { 回调函数"onXX", 参数"argd":{"tbpu.xx", "ocr.xx"} }
    # msnPath: 单个文档路径
    # pageRange: 页数范围。可选： None 全部页 , [1,3] 页面范围（含开头结束）。
    # pageList: 指定多个页数。可选： [] 使用pageRange设置 , [1,2,3] 指定页数
    # password: 密码（非必填）
    def addMission(self, msnInfo, msnPath, pageRange=None, pageList=[], password=""):
        try:
            doc = fitz.open(msnPath)
        except Exception as e:
            return f"[Error] fitz.open error: {msnPath} {e}"
        if doc.isEncrypted and not doc.authenticate(password):
            if password:
                msg = f"[Error] Incorrect password. 文档已加密，密码错误。 [{password}]"
            else:
                msg = "[Error] Doc encrypted. 文档已加密，请提供密码。"
            return msg
        msnInfo["doc"] = doc
        msnInfo["path"] = msnPath
        # 使用 pageRange 的页面范围
        if len(pageList) == 0:
            if isinstance(pageRange, (tuple, list)) and len(pageRange) == 2:
                a, b = pageRange[0], pageRange[1]
                if a < 1:
                    return f"[Error] pageRange {pageRange} 范围起始不能小于1"
                if b > doc.page_count:
                    return f"[Error] pageRange {pageRange} 范围结束不能大于页数 {doc.page_count}"
                if a > b:
                    return f"[Error] pageRange {pageRange} 范围错误"
                pageList = list(range(a - 1, b))
            else:
                pageList = list(range(0, doc.page_count))
        # 检查页数列表合法性
        if len(pageList) == 0:
            return "[Error] 页数列表为空"
        if not all(isinstance(item, int) for item in pageList):
            return "[Error] 页数列表内容非整数"
        return self.addMissionList(msnInfo, pageList)

    def msnTask(self, msnInfo, pno):  # 执行msn。pno为当前页数
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

    # 获取一个文档的信息，如页数
    def getDocInfo(self, path):
        try:
            with FitzOpen(path) as doc:
                info = {
                    "path": path,
                    "page_count": doc.page_count,
                    "is_encrypted": doc.isEncrypted,
                }
                return info
        except Exception as e:
            return {"path": path, "error": e}


# 全局 DOC 任务管理器
MissionDOC = _MissionDocClass()
