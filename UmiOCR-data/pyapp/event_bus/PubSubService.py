# ============================================
# =============== 发布/订阅模式 ===============
# ============================================

from PySide2.QtCore import QObject, Slot, Signal, QMutex, QThread, QCoreApplication


# 发布/订阅 服务类
class PubSubServiceClass(QObject):
    def __init__(self):
        # 事件字典，元素为 回调函数列表
        self.__eventDict = {}
        self.__eventDictMutex = QMutex()  # 事件字典的锁
        # 信号
        self.__eventSignal = self.__EventSignal()
        self.__eventSignal.signal.connect(self.__publish)

    # ========================= 【接口】 =========================

    # 订阅事件
    def subscribe(self, title, func):
        self.__eventDictMutex.lock()  # 上锁
        if title not in self.__eventDict:
            self.__eventDict[title] = [func]
        else:
            self.__eventDict[title].append([func])
        self.__eventDictMutex.unlock()  # 解锁
        print("== 加入订阅：", title, self.__eventDict[title])

    # 取消订阅事件
    def unsubscribe(self, title, func):
        # 将回调函数从 对应标题的事件列表中 移除
        self.__eventDictMutex.lock()  # 上锁
        if title in self.__eventDict:
            l = self.__eventDict[title]
            if func in l:
                l.remove(func)
        self.__eventDictMutex.unlock()  # 解锁
        print("== 取消订阅：", title, self.__eventDict[title])

    # 发布事件
    def publish(self, title, *args):
        # 在主线程调用
        if QThread.currentThread() == QCoreApplication.instance().thread():
            print("== 主线程 发布消息：", title, args)
            self.__publish(title, args)
        # 在子线程调用
        else:
            print("== 子线程 发布消息：", title, args)
            self.__eventSignal.signal.emit(title, args)

    # ========================= 【实现】 =========================

    # 发布事件的实现（主线程）
    @Slot(str, "QVariant")
    def __publish(self, title, args):
        self.__eventDictMutex.lock()  # 上锁
        if title not in self.__eventDict:
            print(f"[Warning] 发布标题{title}不存在事件字典中！")
        else:
            l = self.__eventDict[title]
            for func in l:
                try:
                    func(*args)
                except Exception as e:
                    print(f"[Error] 发送事件异常。\n{title} - {args}\n{e}")
        self.__eventDictMutex.unlock()  # 解锁

    # 信号类
    class __EventSignal(QObject):
        signal = Signal(str, "QVariant")


# 发布/订阅 服务单例
PubSubService = PubSubServiceClass()
