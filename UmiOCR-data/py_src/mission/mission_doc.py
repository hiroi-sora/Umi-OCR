# ===============================================
# =============== 文档 - 任务管理器 ===============
# ===============================================

# API所有页数page 均为1开始

from .mission import Mission
from .mission_ocr import MissionOCR
from ..ocr.tbpu import getParser
from ..ocr.tbpu import IgnoreArea
from ..ocr.tbpu.parser_tools.paragraph_parse import word_separator  # 上下句间隔符

import fitz  # PyMuPDF
import time
from PIL import Image
from io import BytesIO

MinSize = 1080  # 最小渲染分辨率


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
        self._minInterval = 0.1  # msnTask最短调用间隔
        self._lastCallTime = 0  # 上一次调用时间

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
        # =============== tbpu文本块后处理 msnInfo["tbpu"] ===============
        argd = msnInfo["argd"]  # 参数
        msnInfo["tbpu"] = []
        msnInfo["ignoreArea"] = {}
        # 忽略区域
        if "tbpu.ignoreArea" in argd:
            iArea = argd["tbpu.ignoreArea"]
            if type(iArea) == list and len(iArea) > 0:
                msnInfo["ignoreArea"]["obj"] = IgnoreArea(iArea)
                # 范围，负数转为倒数第x页
                igStart = argd.get("tbpu.ignoreRangeStart", 1)
                igEnd = argd.get("tbpu.ignoreRangeEnd", doc.page_count)
                if igStart < 0:
                    igStart += doc.page_count + 1
                if igEnd < 0:
                    igEnd += doc.page_count + 1
                msnInfo["ignoreArea"]["start"] = igStart - 1  # -1是将起始1页转为起始0页
                msnInfo["ignoreArea"]["end"] = igEnd - 1
                print(f"忽略区域范围： {igStart} ~ {igEnd}")
        # 获取排版解析器对象
        if "tbpu.parser" in argd:
            msnInfo["tbpu"].append(getParser(argd["tbpu.parser"]))
        return self.addMissionList(msnInfo, pageList)

    def msnTask(self, msnInfo, pno):  # 执行msn。pno为当前页数
        doc = msnInfo["doc"]  # 文档对象
        page = doc[pno]  # 页面对象
        argd = msnInfo["argd"]  # 参数
        extractionMode = argd["doc.extractionMode"]  # OCR内容模式
        """ mixed - 混合OCR/拷贝文本
            fullPage - 整页强制OCR
            imageOnly - 仅OCR图片
            textOnly - 仅拷贝原有文本 """
        errMsg = ""  # 本次任务流程的异常信息

        # =============== 提取图片和原文本 ===============
        imgs = []  # 待OCR的图片列表
        tbs = []  # text box 文本块列表
        if extractionMode == "fullPage":  # 模式：整页强制OCR
            # 检查页面边长，如果低于阈值，则增加放大系数，以提高渲染清晰度
            rect = page.rect
            w, h = abs(rect[2] - rect[0]), abs(rect[3] - rect[1])
            m = min(w, h)
            if m < MinSize:
                zoom = MinSize / max(m, 1)
                matrix = fitz.Matrix(zoom, zoom)
            else:
                zoom = 1
                matrix = fitz.Identity
            p = page.get_pixmap(matrix=matrix)
            bytes = p.tobytes("png")
            imgs.append({"bytes": bytes, "xy": (0, 0), "scale": 1 / zoom})
        else:
            # 获取元素 https://pymupdf.readthedocs.io/en/latest/_images/img-textpage.png
            # 确保越界图像能被采集 https://github.com/pymupdf/PyMuPDF/issues/3171
            p = page.get_text("dict", clip=fitz.INFINITE_RECT())
            for t in p["blocks"]:  # 遍历区块（段落）
                # 图片
                if t["type"] == 1 and (
                    extractionMode == "imageOnly" or extractionMode == "mixed"
                ):
                    bbox = t["bbox"]
                    # 图片视觉大小
                    w1, h1 = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    # 图片实际大小
                    with Image.open(BytesIO(t["image"])) as pimg:
                        w2, h2 = pimg.size
                    scale = w1 / w2  # 图片缩放比例

                    imgs.append(
                        {"bytes": t["image"], "xy": (bbox[0], bbox[1]), "scale": scale}
                    )
                # 文本
                elif t["type"] == 0 and (
                    extractionMode == "textOnly" or extractionMode == "mixed"
                ):
                    l = len(t["lines"]) - 1
                    for index, line in enumerate(t["lines"]):  # 遍历每一行
                        text = ""
                        for span in line["spans"]:  # 遍历每一文本块
                            text += span["text"]
                        if text:
                            b = line["bbox"]
                            tb = {
                                "box": [
                                    [b[0], b[1]],
                                    [b[2], b[1]],
                                    [b[2], b[3]],
                                    [b[0], b[3]],
                                ],
                                "text": text,
                                "score": 1,
                                "end": "\n" if index == l else "",  # 结尾符
                                "from": "text",  # 来源：直接提取文本
                            }
                            tbs.append(tb)
        # 补充结尾符
        for i1 in range(len(tbs) - 1):
            if tbs[i1]["end"]:  # 跳过已有结尾符的
                continue
            i2 = i1 + 1
            sep = word_separator(tbs[i1]["text"][-1], tbs[i2]["text"][0])
            tbs[i1]["end"] = sep

        # =============== 调用OCR，将 imgs 的内容提取出来放入 tbs ===============
        if imgs:
            # 提取 "ocr." 开头的参数，组装OCR参数字典
            ocrArgd = {}
            for k in argd:
                if k.startswith("ocr."):
                    ocrArgd[k] = argd[k]
            # 调用OCR，堵塞等待任务完成
            ocrList = MissionOCR.addMissionWait(ocrArgd, imgs)
            # 整理OCR结果
            for o in ocrList:
                res = o["result"]
                if res["code"] == 100:
                    x, y = o["xy"]
                    scale = o["scale"]
                    for r in res["data"]:
                        # 将图片相对坐标 转为 页面绝对坐标
                        for bi in range(4):
                            r["box"][bi][0] = r["box"][bi][0] * scale + x
                            r["box"][bi][1] = r["box"][bi][1] * scale + y
                        r["from"] = "ocr"  # 来源：OCR
                        tbs.append(r)
                elif res["code"] != 101:
                    errMsg += f'[Error] OCR code:{res["code"]} msg:{res["data"]}\n'

        # =============== tbpu文本块后处理 ===============
        # 忽略区域
        if msnInfo["ignoreArea"]:
            # 检查范围
            igStart = msnInfo["ignoreArea"]["start"]
            igEnd = msnInfo["ignoreArea"]["end"]
            if pno >= igStart and pno <= igEnd:
                tbs = msnInfo["ignoreArea"]["obj"].run(tbs)
        # 其他tbpu
        if msnInfo["tbpu"]:
            for tbpu in msnInfo["tbpu"]:
                tbs = tbpu.run(tbs)

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

        # ===== 仅提取文本时任务速度过快，频繁回调会导致UI卡死，因此故意引入延迟 =====
        currentTime = time.time()
        elapsedTime = currentTime - self._lastCallTime
        # 如果与上一次调用的时间差小于最短间隔，则睡至满足最短间隔
        if elapsedTime < self._minInterval:
            t = self._minInterval - elapsedTime
            time.sleep(t)
        self._lastCallTime = currentTime
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
