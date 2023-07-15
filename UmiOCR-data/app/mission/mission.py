# ==============================================
# =============== 任务管理器 基类 ===============
# ==============================================


from PySide2.QtCore import QMutex, QThreadPool, QRunnable
from uuid import uuid4  # 唯一ID
import threading  # TODO: 测试


class Mission:
    def __init__(self):
        self.__msnDict = {}  # 任务队列的字典，每一项key为id，value为任务队列
        self.__msnMutex = QMutex()  # 任务队列的锁
        self.__task = None  # 异步任务对象
        self.__taskMutex = QMutex()  # 任务对象的锁
        self.__threadPool = QThreadPool.globalInstance()  # 全局线程池

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

    def __taskRun(self):  # 异步执行任务字典的流程
        print(f"线程{threading.current_thread().ident}，__taskRun 任务正在运行~~")
        dictIndex = 0  # 当前取任务字典中的第几个任务队列
        # 循环，直到任务队列的列表为空
        while True:
            # 1. 检查api和任务字典是否为空
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

            # 4. 检查、更新参数
            if not self.msnUpdate():
                print("【Error】任务管理器：msnUpdate失败")
                break  # 更新失败

            # 5. 首次任务
            if msnInfo["state"] == 0:
                msnInfo["state"] = 1
                msnInfo["onStart"]()

            # 6. 执行任务
            res = self.msnTask(msnInfo)
            if res == None:
                print("【Error】任务管理器：msnTask失败")
                continue

            # 7. 再次检查任务是否要求停止
            if msnInfo["state"] == -1:
                self.__msnDictDel(dictKey)
                continue

            # 8. 不停止，则上报该任务
            msnInfo["list"].pop(0)  # 弹出该任务
            msnInfo["onGet"](f"执行结果：{res}")  # 回调

            # 9. 这条任务队列完成
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
        self.__taskMutex.lock()  # 上锁
        self.__task = None
        self.__taskMutex.unlock()  # 解锁

    # ========================= 【继承重载】 =========================

    def msnUpdate(self):  # 用于更新api和参数
        print("mission 父类 msnUpdate")
        return False

    def msnTask(self, msnInfo):  # 执行msnInfo中第一个任务
        print("mission 父类 msnTask")
        return None

    # ========================= 【异步类】 =========================

    class __Task(QRunnable):
        def __init__(self, taskFunc):
            super().__init__()
            self.__taskFunc = taskFunc

        def run(self):
            self.__taskFunc()
