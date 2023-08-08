# ============================================
# =============== 发布/订阅模式 ===============
# ============================================

from PySide2.QtCore import QObject, Slot, Signal, QMutex, QThread, QCoreApplication


# 发布/订阅 服务类
class __PubSubServiceClass:
    def __init__(self):
        # 事件字典，元素为 回调函数列表
        self.__eventDict = {}
        self.__eventDictMutex = QMutex()  # 事件字典的锁
        # 组字典，元素为 组列表。可以成组取消订阅，方便管理。
        self.__groupDict = {}
        self.__groupDictMutex = QMutex()  # 组字典的锁
        # 信号
        self.__eventSignal = self.__EventSignal()
        self.__eventSignal.signal.connect(self.__publish)

    # ========================= 【接口】 =========================

    # 订阅事件
    def subscribe(self, title, func):
        if not callable(func):
            print(f"[Error] 订阅事件失败！{func} 不可调用。")
            return
        self.__eventDictMutex.lock()  # 上锁
        if title not in self.__eventDict:
            self.__eventDict[title] = [func]
        else:
            self.__eventDict[title].append(func)
        self.__eventDictMutex.unlock()  # 解锁

    # 订阅事件，可额外传入组名，以便管理。
    def subscribeGroup(self, title, func, groupName):
        self.__groupDictMutex.lock()  # 上锁
        if groupName not in self.__groupDict:
            self.__groupDict[groupName] = [(title, func)]
        else:
            self.__groupDict[groupName].append((title, func))
        self.__groupDictMutex.unlock()  # 解锁
        self.subscribe(title, func)

    # 取消订阅事件
    def unsubscribe(self, title, func):
        if not callable(func):
            print(f"[Error] 取消订阅事件失败！{func} 不可调用。")
            return
        # 将回调函数从 对应标题的事件列表中 移除
        self.__eventDictMutex.lock()  # 上锁
        if title in self.__eventDict:
            l = self.__eventDict[title]
            if func in l:
                l.remove(func)
        self.__eventDictMutex.unlock()  # 解锁

    # 取消订阅某个组的所有事件
    def unsubscribeGroup(self, groupName):
        self.__groupDictMutex.lock()  # 上锁
        if groupName in self.__groupDict:
            l = self.__groupDict[groupName]
            for i in l:
                self.unsubscribe(i[0], i[1])
            self.__groupDict[groupName] = []
        self.__groupDictMutex.unlock()  # 解锁

    # 发布事件
    def publish(self, title, *args):
        # 在主线程调用
        if QThread.currentThread() == QCoreApplication.instance().thread():
            self.__publish(title, args)
        # 在子线程调用
        else:
            self.__eventSignal.signal.emit(title, args)

    # ========================= 【实现】 =========================

    # 发布事件的实现（主线程）
    @Slot(str, "QVariant")
    def __publish(self, title, args):
        l = []
        self.__eventDictMutex.lock()  # 上锁
        if title not in self.__eventDict:
            pass
        else:
            l = self.__eventDict[title].copy()  # 拷贝一份
        self.__eventDictMutex.unlock()  # 解锁
        for func in l:
            try:
                func(*args)
            except Exception as e:
                print(f"[Error] 发送事件异常。{e}\n原始信息： {title} - {args}\nfunc：{func}")

    # 信号类
    class __EventSignal(QObject):
        signal = Signal(str, "QVariant")


# 发布/订阅 服务单例
PubSubService = __PubSubServiceClass()
