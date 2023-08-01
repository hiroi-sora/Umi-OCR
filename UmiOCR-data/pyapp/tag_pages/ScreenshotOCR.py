# ========================================
# =============== 截图OCR页 ===============
# ========================================

from .page import Page  # 页基类
from ..utils.image_provider import PixmapProvider  # 图片提供器
from ..mission.mission_ocr import MissionOCR  # 任务管理器

from PySide2.QtGui import QGuiApplication  # 截图


class ScreenshotOCR(Page):
    # ========================= 【qml调用python】 =========================

    def screenshot(self):  # 开始截图
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
        return grabList

    # 截图完毕，提交OCR，并返回裁切结果
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
        if "allImgID" in argd:  # 删除完整图片的缓存
            PixmapProvider.delPixmap(argd["allImgID"])
        self.__msnPixmap(pixmap, configDict)  # 开始OCR
        return clipID

    # ========================= 【OCR 任务控制】 =========================

    def __msnPixmap(self, pixmap, configDict):  # 接收路径列表和配置参数字典，开始OCR任务
        # 任务信息
        msnInfo = {
            "onStart": self.__onStart,
            "onReady": self.__onReady,
            "onGet": self.__onGet,
            "onEnd": self.__onEnd,
            "argd": configDict,
        }
        # 图片转字节，加入任务队列
        bytesData = PixmapProvider.toBytes(pixmap)
        msnList = [{"bytes": bytesData}]
        self.msnID = MissionOCR.addMissionList(msnInfo, msnList)
        if self.msnID:  # 添加成功，通知前端刷新UI
            print(f"添加任务成功 {self.msnID}\n")
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
        print(f"OCR完成， {res}")

    def __onEnd(self, msnInfo, msg):  # 任务队列完成或失败
        # msg: [Success] [Warning] [Error]
        pass
