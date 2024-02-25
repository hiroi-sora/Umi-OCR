# 提供在主线程中调用指定函数

from PySide2.QtCore import QObject, Slot, Signal, QTimer, QMutex
from uuid import uuid4  # 唯一ID


class __CallFunc(QObject):
    def __init__(self):
        super().__init__()
        # 信号 在主线程中调用函数
        self._callFuncSignal = self.cSignal()
        self._callFuncSignal.signal.connect(self._cFunc)
        # 计时器停止字典
        self._timerStopDict = {}
        self._timerLock = QMutex()

    # ========================= 【接口】 =========================

    # 立刻：在主线程中调用python函数
    def now(self, func, *args):
        self._callFuncSignal.signal.emit((func, args))

    # 延时：在主线程中调用python函数。返回计时器ID
    def delay(self, func, time, *args):
        timerID = str(uuid4())

        def go():
            timer = QTimer(self)
            timer.setSingleShot(True)  # 单次运行
            timer.timeout.connect(lambda: self._timerFunc(timerID, func, args))
            timer.start(time * 1000)

        self.now(go)
        return timerID

    # 取消已启用的延时
    def delayStop(self, timerID):
        self._timerLock.lock()
        self._timerStopDict[timerID] = True  # 记录停止
        self._timerLock.unlock()

    # ==================================================
    # 计时器调用的函数
    def _timerFunc(self, timerID, func, args):
        self._timerLock.lock()
        if timerID in self._timerStopDict:
            del self._timerStopDict[timerID]
            self._timerLock.unlock()
            return
        self._timerLock.unlock()
        func(*args)

    # 异步调用的槽函数
    @Slot("QVariant")
    def _cFunc(self, args):
        args[0](*args[1])

    # 信号类
    class cSignal(QObject):
        signal = Signal("QVariant")


CallFunc = __CallFunc()
