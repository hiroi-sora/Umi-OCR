# ========================================
# =============== 截图OCR页 ===============
# ========================================

from .page import Page  # 页基类
from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..mission.mission_ocr import MissionOCR  # 任务管理器
from ..utils.utils import findImages

from PySide2.QtGui import QGuiApplication, QClipboard, QImage, QPixmap  # 截图 剪贴板
import time

Clipboard = QClipboard()  # 剪贴板


class ScreenshotOCR(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.msnDict = {}
        self.recentResult = None  # 缓存最后一次识别结果

    # ========================= 【qml调用python】 =========================

    # 对一个imgID进行OCR
    def ocrImgID(self, imgID, configDict):
        pixmap = PixmapProvider.getPixmap(imgID)
        if not pixmap:
            e = f'[Error] ScreenshotOCR: imgID "{imgID}" does not exist in the PixmapProvider dict.'
            return e
        self.__msnImage(pixmap, imgID, configDict)  # 开始OCR
        return "[Success]"

    # 开始粘贴
    def paste(self, configDict):
        self.recentResult = None
        # 获取剪贴板数据
        mime_data = Clipboard.mimeData()
        res = {}  # 结果字典
        # 检查剪贴板的内容，若是图片，则提取它并扔给OCR
        if mime_data.hasImage():
            image = Clipboard.image()
            pixmap = QPixmap.fromImage(image)
            pasteID = PixmapProvider.addPixmap(pixmap)  # 存入提供器
            self.__msnImage(image, pasteID, configDict)
            res["imgID"] = pasteID
        # 若为URL
        elif mime_data.hasUrls():
            urlList = mime_data.urls()
            paths = []
            for url in urlList:  # 遍历URL列表，提取其中的文件
                if url.isLocalFile():
                    p = url.toLocalFile()
                    paths.append(p)
            paths = findImages(paths, False)  # 过滤，保留图片的路径
            if len(paths) == 0:  # 没有有效图片
                res["error"] = "[Warning] No image in clipboard."
            else:  # 将有效图片地址传入OCR，返回地址列表
                self.__msnPaths(paths, configDict)
                res["paths"] = paths
        elif mime_data.hasText():
            res["error"] = "[Warning] No image in clipboard."
        else:
            res["error"] = "[Warning] No image in clipboard."
        if "error" in res:
            self.recentResult = {"code": 102, "data": res["error"]}
        return res  # 返回结果字典

    # 停止全部任务
    def msnStop(self):
        self.callQml("setMsnState", "none")
        for i in self.msnDict:
            MissionOCR.stopMissionList(i)
        self.msnDict = {}

    # ========================= 【OCR 任务控制】 =========================

    # 传入 QImage或QPixmap图片， 图片id， 配置字典。 提交OCR任务。
    def __msnImage(self, img, imgID, configDict):
        # 图片转字节，构造任务队列
        bytesData = PixmapProvider.toBytes(img)
        msnList = [{"bytes": bytesData, "imgID": imgID}]
        self.__msn(msnList, configDict)

    # 传入路径列表，提交OCR任务，返回图片缓存ID
    def __msnPaths(self, paths, configDict):
        msnList = [{"path": x} for x in paths]
        self.__msn(msnList, configDict)

    # 开始任务
    def __msn(self, msnList, configDict):
        # 任务信息
        msnInfo = {
            "onStart": self.__onStart,
            "onReady": self.__onReady,
            "onGet": self.__onGet,
            "onEnd": self.__onEnd,
            "argd": configDict,
        }
        msnID = MissionOCR.addMissionList(msnInfo, msnList)
        if msnID:  # 添加成功
            self.msnDict[msnID] = None
            self.callQml("setMsnState", "run")
        else:  # 添加任务失败
            self.__onEnd(None, "[Error] Failed to add task.\n【错误】添加任务失败。")

    def __onStart(self, msnInfo):  # 任务队列开始
        pass

    def __onReady(self, msnInfo, msn):  # 单个任务准备
        pass

    def __onGet(self, msnInfo, msn, res):  # 单个任务完成
        # 补充平均置信度
        score = 0
        num = 0
        if res["code"] == 100:
            for r in res["data"]:
                score += r["score"]
                num += 1
            if num > 0:
                score /= num
        res["score"] = score
        # 通知qml更新UI
        imgID = msn.get("imgID", "")
        imgPath = msn.get("path", "")
        self.recentResult = res  # 记录最后一次结果
        self.callQmlInMain("onOcrGet", res, imgID, imgPath)  # 在主线程中调用qml

    def __onEnd(self, msnInfo, msg):  # 任务队列完成或失败
        # msg: [Success] [Warning] [Error]

        def update():
            # 清除任务id
            if msnInfo["msnID"] in self.msnDict:
                del self.msnDict[msnInfo["msnID"]]
            # 所有任务都完成了
            if not self.msnDict:
                # 停止前端显示
                self.callQml("setMsnState", "none")
            self.callQml("onOcrEnd", msg)

        self.callFunc(update)  # 在主线程中执行

    # 获取最近一次结果
    def getRecentResult(self):
        return self.recentResult
