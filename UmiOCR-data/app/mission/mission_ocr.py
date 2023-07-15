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
        "list": paths,  # 任务队列
    }
    MissionOCR.addMissionList(mission)
"""

from PySide2.QtCore import QMutex, QThreadPool, QRunnable
from uuid import uuid4  # 唯一ID
import threading  # TODO: 测试


class __MissionOcrClass:
    def __init__(self):
        self.__msnDict = {}  # 任务队列的字典，每一项key为id，value为任务队列
        self.__msnMutex = QMutex()  # 任务队列的锁
        self.__task = None  # 异步任务对象
        self.__taskMutex = QMutex()  # 任务对象的锁
        self.__threadPool = QThreadPool.globalInstance()  # 全局线程池
        self.__api = None  # 当前引擎api对象
        self.__args = {}  # 记录当前参数

    # ========================= 【调用接口】 =========================

    def addMissionList(self, msnInfo):  # 添加一条任务队列，返回任务ID
        msnID = uuid4()
        # state: 0等待开始，1进行中，-1要求停止
        msnInfo["state"] = 0
        # 添加到任务队列
        self.__msnMutex.lock()  # 上锁
        self.__msnDict[msnID] = msnInfo  # 添加任务
        self.__msnMutex.unlock()  # 解锁
        # 启动任务
        self.__startMsns()
        # 返回任务id
        return msnID

    def stopMissionList(self, msnID):  # 停止一条任务队列，返回剩余未执行的任务
        leftover = None
        self.__msnMutex.lock()  # 上锁
        if msnID in self.__msnDict:
            leftover = self.__msnDict[msnID]["list"]
            self.__msnDict[msnID]["state"] = -1  # 设为停止状态
        self.__msnMutex.unlock()  # 解锁
        return leftover

    # ========================= 【主线程 方法】 =========================

    def __startMsns(self):  # 启动异步任务，执行所有任务列表
        # 若当前异步任务对象为空，则创建工作线程
        self.__taskMutex.lock()  # 上锁
        if self.__task == None:
            self.__task = self.__Task(self.__taskRun)
            self.__threadPool.start(self.__task)
        self.__taskMutex.unlock()  # 解锁

    # ========================= 【子线程 方法】 =========================

    def __taskRun(self):  # 异步执行
        print(f"线程{threading.current_thread().ident}，__taskRun 任务正在运行~~")
        dictIndex = 0  # 当前取任务字典中的第几个任务队列
        # 循环，直到任务队列的列表为空
        while True:
            # 1. 检查是否为空
            self.__msnMutex.lock()  # 上锁
            dl = len(self.__msnDict)  # 任务字典长度
            if dl == 0:  # 任务字典已空
                self.__msnMutex.unlock()  # 解锁
                break

            # 2. 取一个任务
            dictIndex = (dictIndex + 1) % dl  # 取一个任务队列
            dictKey = tuple(self.__msnDict.keys())[dictIndex]
            msnInfo = self.__msnDict[dictKey]
            self.__msnMutex.unlock()  # 解锁

            # 3. 检查任务是否要求停止
            if msnInfo["state"] == -1:
                self.__msnDictDel(dictKey)
                continue

            # 4. 首次任务
            if msnInfo["state"] == 0:
                msnInfo["state"] = 1
                msnInfo["onStart"]()

            # 5. 执行任务
            msn = msnInfo["list"][0]  # 取第一个任务
            # TODO: 执行
            import time

            time.sleep(1)
            res = "2333"

            # 6. 再次检查任务是否要求停止
            if msnInfo["state"] == -1:
                self.__msnDictDel(dictKey)
                continue

            # 7. 不停止，则上报该任务
            msnInfo["list"].pop(0)  # 弹出该任务
            msnInfo["onGet"](f"执行结果：{res}")  # 回调

            # 8. 这条任务队列完成
            if len(msnInfo["list"]) == 0:
                msnInfo["onFinish"]()
                self.__msnDictDel(dictKey)
                dictIndex -= 1  # 字典下标回退1位，下次执行正确的下一项

        # 完成
        self.__taskFinish()

    def __msnDictDel(self, dictKey):  # 停止 self.__msnDict[dictKey]
        print(f"停止任务字典{dictKey}")
        del self.__msnDict[dictKey]

    def __taskFinish(self):  # 任务结束
        print(f"线程{threading.current_thread().ident}，__taskFinish 任务完成~~")
        self.__taskMutex.lock()  # 上锁
        self.__task = None
        self.__taskMutex.unlock()  # 解锁

    # ========================= 【异步类】 =========================

    class __Task(QRunnable):
        def __init__(self, taskFunc):
            super().__init__()
            self.__taskFunc = taskFunc

        def run(self):
            self.__taskFunc()


# 全局 OCR任务管理器
MissionOCR = __MissionOcrClass()
