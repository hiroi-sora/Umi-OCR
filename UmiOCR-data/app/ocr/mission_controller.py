# ============================================
# =============== OCR任务控制器 ===============
# ============================================

from .api_paddleocr import ApiPaddleOCR

from enum import Enum
import time
from PySide2.QtCore import QMutex, QThreadPool, QObject, QRunnable, Signal, Slot

# 设置任务状态 setMsnState ：
#     none  不在运行
#     init  正在启动
#     run   工作中
#     stop  停止中


class Mission(QObject):
    __msnCallback = Signal("QVariant", "QVariant")  # 给任务调用方回调的信号
    __setMsnState = Signal(str)  # 设置任务状态的信号

    def __init__(self, setMsnState):
        super().__init__()
        self.__missions = []  # 任务列表
        self.__msnMutex = QMutex()  # 任务列表的锁
        self.__msnTask = None  # 异步任务对象
        self.__threadPool = QThreadPool.globalInstance()  # 全局线程池
        self.__setMsnState.connect(setMsnState)  # 设置任务状态的回调
        self.__api = None  # 当前引擎api对象
        self.__args = {}  # 记录当前参数

    # ========================= 【任务列表前后处理】 =========================

    def __runStart(self):  # 开始
        self.__setMsnState.emit("init")
        # TODO: 初始化步骤
        self.__setMsnState.emit("run")

    def __runEnd(self):  # 结束
        self.__setMsnState.emit("stop")
        # TODO: 结束清理步骤
        self.__setMsnState.emit("none")

    # ========================= 【运行单个任务，返回结果】 =========================

    def __runPath(self, path):  # 图片路径任务
        import time

        time.sleep(1)
        return {"code": 100, "data": []}

    def __runBytes(self, bytes):  # 图片字节流任务
        print(f"字节流识图{bytes}")

    def __runClipboard(self):  # 剪贴板任务
        print(f"剪贴板识图")

    # ========================= 【调用接口】 =========================

    def add(self, mission):  # 添加任务，并开始执行
        """添加一个或多个异步OCR任务，或更改参数指令。\n
        `mission` 为单个字典或字典列表：\n
        {
        任务模式下，必填一项\n
            "path":      "图片路径，字符串",\n
            "bytes":     图片字节流,\n
            "clipboard": None 标记为剪贴板任务，值留空,\n
        任务模式下，必填\n
            "callback":  回调函数 (res, msn)
        指定参数\n
            "api":       "api代号"，必须同时填args,\n
            "args":      "api参数",\n
        }
        """
        checkKeys = ("path", "bytes", "clipboard")
        if isinstance(mission, dict):
            mission = [mission]
        # ========== 检测参数合法性 ==========
        if not isinstance(mission, list):
            raise ValueError("mission 类型错误，必须为字典或列表")
        for m in mission:
            msnKeys = set(m.keys())
            kList = msnKeys.intersection(checkKeys)
            kListLen = len(kList)
            if kListLen > 1:
                raise ValueError(f"mission 参数错误，任务参数仅需要含一个：{checkKeys} 。")
            elif kListLen == 1:
                if not "callback" in msnKeys:
                    raise ValueError("mission 参数错误，任务模式必须含回调函数callback。")
                if not callable(m["callback"]):
                    raise ValueError("mission 参数错误，callback必须为回调函数。")
            else:
                if "api" not in msnKeys or "args" not in msnKeys:
                    raise ValueError("mission 参数错误，指令模式下必须含有 api 或 args 。")
                if "api" in msnKeys and "args" not in msnKeys:
                    raise ValueError("mission 参数错误，指定 api 必须同时指定 args 。")
        if len(mission) <= 0:
            print("【Warning】传入任务列表为空。")
            return
        # ========== 加入任务列表 ==========
        self.__msnMutex.lock()  # 上锁
        self.__missions.extend(mission)  # 添加任务
        self.__msnMutex.unlock()  # 解锁
        # 如果当前没有在运行的工作线程，则创建工作线程
        if self.__msnTask == None:
            self.__msnTask = self.__Task(self.__runMissions)
            self.__msnTask.worker.finished.connect(self.__onFinished)
            self.__threadPool.start(self.__msnTask)

    def stop(self):  # 暂停当前任务列表
        pass

    def clear(self):  # 清空当前任务列表
        pass

    def exit(self):  # 关闭任务控制器
        pass

    # ========================= 【任务循环的逻辑】 =========================

    class __Task(QRunnable):  # 异步类
        class __Worker(QObject):  # 信号类
            finished = Signal()  # 任务完成的信号

        def __init__(self, runFunc):
            super().__init__()
            self.worker = self.__Worker()
            self.__runFunc = runFunc

        def run(self):
            self.__runFunc()
            self.worker.finished.emit()  # 发送完成信号

    def __runMissions(self):  # 运行OCR任务列表
        self.__runStart()
        # 循环，直到任务列表为空
        while True:
            # 1. 从任务列表中取一个任务
            self.__msnMutex.lock()  # 上锁
            if len(self.__missions) == 0:  # 任务列表已空
                self.__msnMutex.unlock()  # 解锁
                break
            msn = self.__missions.pop(0)  # 取第一个任务
            self.__msnMutex.unlock()  # 解锁
            # 2. 设置参数
            keys = msn.keys()
            if "api" in keys:
                self.__startApi(msn["api"], msn["args"])
            elif "args" in keys:
                self.__setArgs(msn["args"])
            # 3.1. 检查引擎
            ocrTime1 = time.time()
            if not self.__api or not self.__api.check():
                res = {"code": 801, "data": "Ocr api not init."}
            # 3.2. 执行OCR任务
            elif "path" in keys:
                res = self.__api.runPath(msn["path"])
            elif "bytes" in keys:
                res = self.__api.runBytes(msn["bytes"])
            elif "clipboard" in keys:
                res = self.__api.runClipboard()
            ocrTime2 = time.time()
            # 4. 执行回调
            if "callback" in keys:
                res["time"] = ocrTime2 - ocrTime1
                self.__msnCallback.connect(msn["callback"])
                self.__msnCallback.emit(res, msn)
                self.__msnCallback.disconnect(msn["callback"])
        self.__runEnd()

    @Slot()
    def __onFinished(self):  # 完成全部任务列表的事件
        self.__msnTask = None  # 删除本次异步任务对象

    def __startApi(self, api, args):  # 启动api
        if self.__api:
            self.__api.stop()
        # TODO: 选择新api
        self.__api = ApiPaddleOCR()
        self.__setArgs(args)

    def __setArgs(self, args):  # 设置api参数
        self.__api.start(args)
