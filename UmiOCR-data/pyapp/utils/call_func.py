# 提供在主线程中调用指定函数

from PySide2.QtCore import QObject, Slot, Signal, QTimer
from uuid import uuid4  # 唯一ID


class __CallFunc(QObject):
    def __init__(self):
        # 信号 在主线程中调用函数
        self.__callFuncSignal = self.cSignal()
        self.__callFuncSignal.signal.connect(self.__cFunc)
        # 计时器字典
        self.timerDict = {}

    # 立刻：在主线程中调用python函数
    def now(self, func, *args):
        self.__callFuncSignal.signal.emit((func, args))

    # 延时：在主线程中调用python函数。返回计时器ID
    def delay(self, func, time, *args):
        def go():
            timer = QTimer()
            timer.setSingleShot(True)  # 单次运行
            # timer.timeout.connect(lambda: self.now(func, *args))
            timer.timeout.connect(lambda: self.__cFunc((func, *args)))
            timer.start(time * 1000)

        self.now(go)

    @Slot("QVariant")
    def __cFunc(self, args):
        print("====================")
        args[0](*args[1])

    # 信号类
    class cSignal(QObject):
        signal = Signal("QVariant")


CallFunc = __CallFunc()
