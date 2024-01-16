# ===============================================
# =============== 文档 - 任务管理器 ===============
# ===============================================

# API所有页数page 均为1开始

from .mission import Mission
from .mission_ocr import MissionOCR
from ..ocr.tbpu import Merge as tbpuMerge
from ..ocr.tbpu import IgnoreArea

import fitz  # PyMuPDF
import time


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
        # =============== 加载文档，获取文档操作对象 ===============
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
        # =============== pageRange 页面范围 ===============
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
        # =============== 段落合并 ===============
        argd = msnInfo["argd"]  # 参数
        msnInfo["tbpu"] = []
        if "tbpu.merge" in argd and argd["tbpu.merge"] != "None":
            if argd["tbpu.merge"] in tbpuMerge:
                msnInfo["tbpu"].append(tbpuMerge[argd["tbpu.merge"]]())
            else:
                print(f'[Error] 段落合并参数不存在： {argd["tbpu.merge"]}')
        # =============== 忽略区域 ===============
        if "tbpu.ignoreArea" in argd:
            iArea = argd["tbpu.ignoreArea"]
            if type(iArea) == list and len(iArea) > 0:
                msnInfo["tbpu"].append(IgnoreArea(iArea))
        return self.addMissionList(msnInfo, pageList)

    def msnTask(self, msnInfo, pno):  # 执行msn。pno为当前页数
        doc = msnInfo["doc"]  # 文档对象
        page = doc[pno]  # 页面对象
        argd = msnInfo["argd"]  # 参数
        ocrMode = argd["doc.ocrMode"]  # OCR内容模式
        """ mixed - 混合OCR/拷贝文本
            fullPage - 整页强制OCR
            imageOnly - 仅OCR图片
            textOnly - 仅拷贝原有文本 """
        errMsg = ""  # 本次任务流程的异常信息

        # =============== 提取图片和原文本 ===============
        imgs = []  # 待OCR的图片列表
        tbs = []  # text box 文本块列表
        if ocrMode == "fullPage":  # 模式：整页强制OCR
            p = page.get_pixmap()
            bytes = p.tobytes("png")
            imgs.append({"bytes": bytes})
        else:
            # 获取元素 https://pymupdf.readthedocs.io/en/latest/_images/img-textpage.png
            p = page.get_text("dict")
            for t in p["blocks"]:
                # 图片
                if t["type"] == 1 and (ocrMode == "imageOnly" or ocrMode == "mixed"):
                    imgs.append({"bytes": t["image"]})
                # 文本
                elif t["type"] == 0 and (ocrMode == "textOnly" or ocrMode == "mixed"):
                    for line in t["lines"]:
                        for span in line["spans"]:
                            tb = {"box": span["bbox"], "text": span["text"], "score": 1}
                            tbs.append(tb)
        # 仅提取文本时任务速度过快，频繁回调会导致UI卡死，因此故意引入延迟
        if ocrMode == "textOnly":
            time.sleep(0.01)

        # =============== 调用OCR，将 imgs 的内容提取出来放入 tbs ===============
        if imgs:
            ocrList = MissionOCR.addMissionWait(argd, imgs)
            for o in ocrList:
                res = o["result"]
                if res["code"] == 100:
                    tbs += res["data"]
                elif res["code"] != 101:
                    errMsg += f'[Error] OCR code:{res["code"]} msg:{res["data"]}\n'

        # =============== 组装结果字典 resDict ===============
        if errMsg:
            errMsg = f"[Error] Doc P{pno}\n" + errMsg
            print(errMsg)

        if tbs:  # 有文本
            resDict = {"code": 100, "data": tbs}
        elif errMsg:  # 无文本，有异常
            resDict = {"code": 102, "data": errMsg}
        else:  # 无文本，无异常
            resDict = {"code": 101, "data": ""}
        return resDict

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
