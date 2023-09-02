# ========================================
# =============== 截图OCR页 ===============
# ========================================

from .page import Page  # 页基类
from ..utils.image_provider import PixmapProvider  # 图片提供器
from ..mission.mission_ocr import MissionOCR  # 任务管理器
from ..utils.utils import findImages
from ..event_bus.key_mouse.keyboard import HotkeyCtrl
from ..event_bus.pubsub_service import PubSubService

from PySide2.QtGui import QGuiApplication, QImage, QPixmap  # 截图 剪贴板


class ScreenshotOCR(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.msnDict = {}
        self.ssImgIDs = []  # 缓存当前完整截屏id
        self.showImgIDs = []  # 缓存当前展示图片id

    # ========================= 【qml调用python】 =========================

    # 开始截图，获取每个屏幕的完整截图，传给qml前端裁切
    def screenshot(self):
        screensList = QGuiApplication.screens()
        grabList = []
        for screen in screensList:
            pixmap = screen.grabWindow(0)  # 截图
            imgID = PixmapProvider.addPixmap(pixmap)  # 存入提供器，获取imgID
            grabList.append(
                {  # 传递信息给qml
                    "imgID": imgID,
                    "screenName": screen.name(),
                }
            )
            self.ssImgIDs.append(imgID)
        return grabList

    # 截图完毕，前端提供裁切数据，py裁切图片并提交OCR，返回裁切小图
    def screenshotEnd(self, argd, configDict):
        pixmap = PixmapProvider.getPixmap(argd["imgID"])
        if not pixmap:
            e = f'[Error] ScreenshotOCR: Key "{argd["imgID"]}" does not exist in the PixmapProvider dict.'
            return e
        x, y, w, h = argd["clipX"], argd["clipY"], argd["clipW"], argd["clipH"]
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            e = f"[Error] ScreenshotOCR: x/y/w/h value error. {x}/{y}/{w}/{h}"
            return e
        pixmap = pixmap.copy(x, y, w, h)  # 进行裁切
        clipID = PixmapProvider.addPixmap(pixmap)  # 存入提供器，获取imgID
        self.showImgIDs.append(clipID)
        # 删除截屏图片的缓存
        PixmapProvider.delPixmap(self.ssImgIDs)
        self.ssImgIDs = []
        self.__msnImage(pixmap, clipID, configDict)  # 开始OCR
        return clipID

    # 开始粘贴
    def paste(self, configDict):
        # 获取剪贴板数据
        mime_data = Clipboard.mimeData()
        res = {}  # 结果字典
        # 检查剪贴板的内容，若是图片，则提取它并扔给OCR
        if mime_data.hasImage():
            image = Clipboard.image()
            pixmap = QPixmap.fromImage(image)
            pasteID = PixmapProvider.addPixmap(pixmap)  # 存入提供器
            self.showImgIDs.append(pasteID)
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
                res["error"] = "[Warning] No image."
            else:  # 将有效图片地址传入OCR，返回地址列表
                self.__msnPaths(paths, configDict)
                res["paths"] = paths
        elif mime_data.hasText():
            res["error"] = "[Warning] No image."
        else:
            res["error"] = "[Warning] No image."
        return res  # 返回结果字典

    # 停止全部任务
    def msnStop(self):
        self.callQml("setMsnState", "none")
        for i in self.msnDict:
            MissionOCR.stopMissionList(i)
        self.msnDict = {}
        PixmapProvider.delPixmap(self.showImgIDs)
        self.showImgIDs = []
        PixmapProvider.delPixmap(self.ssImgIDs)
        self.ssImgIDs = []

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
                # 删除缓存列表中除了最后一项以外的图片。最后一项可能正在展示中所以不能删
                PixmapProvider.delPixmap(self.showImgIDs[:-1])
                del self.showImgIDs[:-1]

        self.callFunc(update)  # 在主线程中执行
