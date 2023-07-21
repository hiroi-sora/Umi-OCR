# ===============================================
# =============== OCR - 任务管理器 ===============
# ===============================================

"""
一种任务管理器为全局单例，不同标签页要执行同一种任务，要访问对应的任务管理器。
任务管理器中有一个引擎API实例，所有任务均使用该API。
标签页可以向任务管理器提交一组任务队列，其中包含了每一项任务的信息，及总体的参数和回调。

添加任务队列的格式
    mission = {
        "onStart": 任务开始回调函数 ,
        "onGet": 获取一项结果回调函数 ,
        "onFinish": 全部完成回调函数 ,
        "onFailure": 失败退出回调函数 ,
        "argd": api参数字典 ,
        "list": paths,  # 任务队列
    }
    MissionOCR.addMissionList(mission)
"""

from ..api.ocr import getApiOcr, isApiOcr
from .mission import Mission


class __MissionOcrClass(Mission):
    def __init__(self):
        super().__init__()
        self.__apiKey = ""  # 当前api类型
        self.__api = None  # 当前引擎api对象

    # ========================= 【重载】 =========================

    def msnPreTask(self, msnInfo):  # 用于更新api和参数
        # TODO: 检查参数更新
        self.__api.start({"exePath": "lib\PaddleOCR-json\PaddleOCR-json.exe"})
        return True

    def msnTask(self, msnInfo, msn):  # 执行msnInfo中第一个任务
        res = self.__api.runPath(msn)
        return res

    # ========================= 【qml接口】 =========================

    def getStatus(self):  # 返回当前状态
        return {
            "apiKey": self.__apiKey,
            "missionListsLength": self.getMissionListsLength(),
        }

    def setApi(self, info):  # 设置api
        # 成功返回 [Success] ，失败返回 [Error] 开头的字符串
        apiKey = info["ocr.api"]
        # 如果api对象已启动，则先停止
        if self.__api:
            self.__api.stop()
        # 获取新api对象
        res = getApiOcr(apiKey, info)
        # 成功
        if isApiOcr(res):
            self.__api = res
            self.__apiKey = apiKey
            return "[Success]"
        # 失败
        else:
            self.__apiKey = ""
            self.__api = None
            if type(res) == str:
                return res
            return "[Error] MissionOCR Failed to setApi, unknown reason"


# 全局 OCR任务管理器
MissionOCR = __MissionOcrClass()
