# ==============================================
# =============== 任务管理器 基类 ===============
# ==============================================


from PySide2.QtCore import QMutex, QThreadPool, QRunnable
from threading import Condition
from uuid import uuid4  # 唯一ID
import time


# 代替 self._threadPool.start ，但是检查线程池是否满，并扩充。
def threadPoolStart(threadPool, *args):
    activeThreadCount = threadPool.activeThreadCount()
    if activeThreadCount >= threadPool.maxThreadCount():
        print(f"[Warning] 线程池已满 {activeThreadCount} ！自动扩充+1。")
        threadPool.setMaxThreadCount(activeThreadCount + 1)
    threadPool.start(*args)


class Mission:
    def __init__(self):
        self._msnInfoDict = {}  # 任务信息的字典
        self._msnListDict = {}  # 任务队列的字典
        self._msnMutex = QMutex()  # 任务队列的锁
        self._task = None  # 异步任务对象
        self._taskMutex = QMutex()  # 任务对象的锁
        self._threadPool = QThreadPool.globalInstance()  # 全局线程池
        # 任务队列调度方式
        # 1111 : 轮询调度，轮流取每个队列的第1个任务
        # 1234 : 顺序调度，将首个队列所有任务处理完，再进入下一个队列
        self._schedulingMode = "1111"

    # ========================= 【调用接口】 =========================

    """
    添加任务队列的格式
    mission = {
        "onStart": 任务队列开始回调函数 , (msnInfo)
        "onReady": 一项任务准备开始 , (msnInfo, msn)
        "onGet": 一项任务获取结果 , (msnInfo, msn, res)
        "onEnd": 任务队列结束 , (msnInfo, msg) // msg可选前缀： [Success] [Warning] [Error]
    }
    MissionOCR.addMissionList(mission, paths)
    """

    # 【异步】添加一条任务队列。成功返回任务ID，失败返回 startswith("[Error]")
    # msnInfo: { 回调函数 "onStart", "onReady", "onGet", "onEnd"}
    # msnList: [ 任务1, 任务2 ]
    def addMissionList(self, msnInfo, msnList):
        if len(msnList) < 1:
            return "[Error] no valid mission in msnList!"
        msnID = str(uuid4())
        # 检查并补充回调函数
        # 队列开始，单个任务准备开始，单任务取得结果，队列结束
        cbKeys = ["onStart", "onReady", "onGet", "onEnd"]
        for k in cbKeys:
            if k not in msnInfo or not callable(msnInfo[k]):
                # print(f"补充空回调函数{k}")
                # msnInfo[k] = (lambda key: lambda *e: print(f"空回调 {key}"))(k)
                msnInfo[k] = lambda *e: None
        # 任务状态state:  waiting 等待开始， running 进行中， stop 要求停止
        msnInfo["state"] = "waiting"
        msnInfo["msnID"] = msnID
        # 添加到任务队列
        self._msnMutex.lock()  # 上锁
        self._msnInfoDict[msnID] = msnInfo  # 添加任务信息
        self._msnListDict[msnID] = msnList  # 添加任务队列
        self._msnMutex.unlock()  # 解锁
        # 启动任务
        self._startMsns()
        # 返回任务id
        return msnID

    # 停止一条任务队列
    def stopMissionList(self, msnID):
        self._msnMutex.lock()  # 上锁
        if msnID in self._msnListDict:
            self._msnInfoDict[msnID]["state"] = "stop"  # 设为停止状态
        self._msnMutex.unlock()  # 解锁

    # 停止全部任务
    def stopAllMissions(self):
        self._msnMutex.lock()  # 上锁
        for msnID in self._msnListDict:
            self._msnInfoDict[msnID]["state"] = "stop"
        self._msnMutex.unlock()  # 解锁

    # 获取每一条任务队列长度
    def getMissionListsLength(self):
        lenDict = {}
        self._msnMutex.lock()
        for k in self._msnListDict:
            lenDict[str(k)] = len(self._msnListDict[k])
        self._msnMutex.unlock()
        return lenDict

    # 【同步】添加一个任务或队列，等待完成，返回任务结果列表。[i]["result"]为结果
    def addMissionWait(self, argd, msnList):
        if not type(msnList) is list:
            msnList = [msnList]
        resList = msnList[:]  # 浅拷贝出一条结果列表
        nowIndex = 0  # 当前处理的任务
        msnLen = len(msnList)
        condition = Condition()  # 线程同步器
        endMsg = ""  # 任务结束的消息

        def _onGet(msnInfo, msn, res):
            nonlocal nowIndex
            resList[nowIndex]["result"] = res
            nowIndex += 1

        def _onEnd(msnInfo, msg):
            nonlocal endMsg
            endMsg = msg
            with condition:  # 释放线程阻塞
                condition.notify()

        def _pass(*x):
            pass

        msnInfo = {
            "onStart": _pass,
            "onReady": _pass,
            "onGet": _onGet,
            "onEnd": _onEnd,
            "argd": argd,
        }
        msnID = self.addMissionList(msnInfo, msnList)
        if msnID.startswith("[Error]"):  # 添加任务失败
            endMsg = msnID
        else:  # 添加成功，线程阻塞，直到任务完成。
            with condition:
                condition.wait()
        # 补充未完成的任务
        for i in range(nowIndex, msnLen):
            if "result" not in resList[i]:
                resList[i]["result"] = {"code": 803, "data": f"任务提前结束。{endMsg}"}
        return resList

    # ========================= 【主线程 方法】 =========================

    def _startMsns(self):  # 启动异步任务，执行所有任务列表
        # 若当前异步任务对象为空，则创建工作线程
        self._taskMutex.lock()  # 上锁
        if self._task == None:
            self._task = self._Task(self._taskRun)
            threadPoolStart(self._threadPool, self._task)
        self._taskMutex.unlock()  # 解锁

    # ========================= 【子线程 方法】 =========================

    def _taskRun(self):  # 异步执行任务字典的流程
        dictIndex = 0  # 当前取任务字典中的第几个任务队列
        # 循环，直到任务队列的列表为空
        while True:
            # 1. 检查api和任务字典是否为空
            self._msnMutex.lock()  # 上锁
            dl = len(self._msnInfoDict)  # 任务字典长度
            if dl == 0:  # 任务字典已空
                self._msnMutex.unlock()  # 解锁
                break

            # 2. 任务调度，取一个任务
            if self._schedulingMode == "1111":  # 轮询
                dictIndex = (dictIndex + 1) % dl
            elif self._schedulingMode == "1234":  # 顺序
                dictIndex = 0  # 始终为首个队列
            dictKey = tuple(self._msnInfoDict.keys())[dictIndex]
            msnInfo = self._msnInfoDict[dictKey]
            msnList = self._msnListDict[dictKey]
            self._msnMutex.unlock()  # 解锁

            # 3. 检查任务是否要求停止
            if msnInfo["state"] == "stop":
                self._msnDictDel(dictKey)
                msnInfo["onEnd"](msnInfo, "[Warning] Task stop.")
                continue

            # 4. 前处理，检查、更新参数
            preFlag = self.msnPreTask(msnInfo)
            if preFlag == "continue":  # 跳过本次
                print("任务管理器：跳过任务")
                continue
            elif preFlag.startswith("[Error]"):  # 异常，结束该队列
                msnInfo["onEnd"](msnInfo, preFlag)
                self._msnDictDel(dictKey)
                dictIndex -= 1  # 字典下标回退1位，下次执行正确的下一项
                continue

            # 5. 首次任务
            if msnInfo["state"] == "waiting":
                msnInfo["state"] = "running"
                msnInfo["onStart"](msnInfo)

            # 6. 执行任务，并记录时间
            msn = msnList[0]
            msnInfo["onReady"](msnInfo, msn)
            t1 = time.time()
            res = self.msnTask(msnInfo, msn)
            t2 = time.time()
            if type(res) == dict:  # 补充耗时和时间戳
                res["time"] = t2 - t1
                res["timestamp"] = t2

            # 7. 再次检查任务是否要求停止
            if msnInfo["state"] == "stop":
                self._msnDictDel(dictKey)
                msnInfo["onEnd"](msnInfo, "[Warning] Task stop.")
                continue

            # 8. 不停止，则上报该任务
            msnList.pop(0)  # 弹出该任务
            msnInfo["onGet"](msnInfo, msn, res)  # 回调

            # 9. 这条任务队列完成
            if len(msnList) == 0:
                msnInfo["onEnd"](msnInfo, "[Success]")
                self._msnDictDel(dictKey)
                dictIndex -= 1  # 字典下标回退1位，下次执行正确的下一项

        # 完成
        self._taskFinish()

    def _msnDictDel(self, dictKey):  # 停止一组任务队列
        # print(f"停止任务字典{dictKey}")
        del self._msnInfoDict[dictKey]
        del self._msnListDict[dictKey]

    def _taskFinish(self):  # 任务结束
        self._taskMutex.lock()  # 上锁
        self._task = None
        self._taskMutex.unlock()  # 解锁

    # ========================= 【继承重载】 =========================

    def msnPreTask(self, msnInfo):  # 任务前处理，用于更新api和参数。
        """返回值可选：
        "" ：空字符串表示正常继续。
        "continue" ：跳过本次任务
        "[Error] xxxx" ：终止这条任务队列，返回异常信息
        """
        # return "[Error] No overloaded msnPreTask. \n【异常】未重载msnPreTask。"
        return ""

    def msnTask(self, msnInfo, msn):  # 执行任务msn，返回结果字典。
        print("mission 父类 msnTask")
        return {"error": f"[Error] No overloaded msnTask. \n【异常】未重载msnTask。"}

    def getStatus(self):  # 返回当前状态
        return "Mission 基类 返回空状态"

    # ========================= 【异步类】 =========================

    class _Task(QRunnable):
        def __init__(self, taskFunc):
            super().__init__()
            self._taskFunc = taskFunc

        def run(self):
            self._taskFunc()
