# ============================================
# =============== 发布/订阅模式 ===============
# ============================================

from PySide2.QtCore import QObject, Slot, Signal, QMutex, QThread, QCoreApplication


# 发布/订阅 服务类
class _PubSubServiceClass:
    def __init__(self):
        # 事件字典，元素为 回调函数列表
        self._eventDict = {}
        self._eventDictMutex = QMutex()  # 事件字典的锁
        # 组字典，元素为 组列表。可以成组取消订阅，方便管理。
        self._groupDict = {}
        self._groupDictMutex = QMutex()  # 组字典的锁
        # 信号
        self._eventSignal = self._EventSignal()
        self._eventSignal.signal.connect(self._publish)

    # ========================= 【接口】 =========================

    # 订阅事件
    def subscribe(self, title, func):
        if not callable(func):
            print(f"[Error] 订阅事件失败！{func} 不可调用。")
            return
        self._eventDictMutex.lock()  # 上锁
        if title not in self._eventDict:
            self._eventDict[title] = [func]
        else:
            self._eventDict[title].append(func)
        self._eventDictMutex.unlock()  # 解锁

    # 订阅事件，可额外传入组名，以便管理。
    def subscribeGroup(self, title, func, groupName):
        self._groupDictMutex.lock()  # 上锁
        if groupName not in self._groupDict:
            self._groupDict[groupName] = [(title, func)]
        else:
            self._groupDict[groupName].append((title, func))
        self._groupDictMutex.unlock()  # 解锁
        self.subscribe(title, func)

    # 取消订阅事件
    def unsubscribe(self, title, func):
        if not callable(func):
            print(f"[Error] 取消订阅事件失败！{func} 不可调用。")
            return
        # 将回调函数从 对应标题的事件列表中 移除
        self._eventDictMutex.lock()  # 上锁
        if title in self._eventDict:
            l = self._eventDict[title]
            if func in l:
                l.remove(func)
        self._eventDictMutex.unlock()  # 解锁

    # 取消订阅某个组的所有事件
    def unsubscribeGroup(self, groupName):
        self._groupDictMutex.lock()  # 上锁
        if groupName in self._groupDict:
            l = self._groupDict[groupName]
            for i in l:
                self.unsubscribe(i[0], i[1])
            self._groupDict[groupName] = []
        self._groupDictMutex.unlock()  # 解锁

    # 发布事件
    def publish(self, title, *args):
        # 在主线程调用
        if QThread.currentThread() == QCoreApplication.instance().thread():
            self._publish(title, args)
        # 在子线程调用
        else:
            self._eventSignal.signal.emit(title, args)

    # ========================= 【实现】 =========================

    # 发布事件的实现（主线程）
    @Slot(str, "QVariant")
    def _publish(self, title, args):
        l = []
        self._eventDictMutex.lock()  # 上锁
        if title not in self._eventDict:
            pass
        else:
            l = self._eventDict[title].copy()  # 拷贝一份
        self._eventDictMutex.unlock()  # 解锁
        for func in l:
            try:
                func(*args)
            except Exception as e:
                print(
                    f"[Error] 发送事件异常。{e}\n原始信息： {title} - {args}\nfunc：{func}"
                )

    # 信号类
    class _EventSignal(QObject):
        signal = Signal(str, "QVariant")


# 发布/订阅 服务单例
PubSubService = _PubSubServiceClass()
