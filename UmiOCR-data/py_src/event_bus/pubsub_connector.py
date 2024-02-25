# ========================================================
# =============== 发布/订阅连接器，在qml调用 ===============
# ========================================================

from PySide2.QtCore import QObject, Slot

from .pubsub_service import PubSubService


class PubSubConnector(QObject):
    def __init__(self, *args):
        super().__init__(*args)
        self._funcDict = {}  # 缓存历史已订阅的函数

    # 订阅事件。传入 标题，函数所在Item，函数名
    @Slot(str, "QVariant", str)
    def subscribe(self, title, item, funcName):
        func = getattr(item, funcName, None)
        if not func:
            print(f"[Error] qml订阅事件失败！未在 {item} 中找到函数 {funcName} 。")
            return
        PubSubService.subscribe(title, func)
        fKey = title + funcName
        self._funcDict[fKey] = func

    # 订阅事件，可额外传入组
    @Slot(str, "QVariant", str, str)
    def subscribeGroup(self, title, item, funcName, groupName):
        func = getattr(item, funcName, None)
        if not func:
            print(f"[Error] qml订阅事件失败！未在 {item} 中找到函数 {funcName} 。")
            return
        PubSubService.subscribeGroup(title, func, groupName)
        fKey = title + funcName
        self._funcDict[fKey] = func

    # 取消订阅事件，由于getattr的不稳定性，因此从历史记录中取函数引用，而不是重新查询。
    @Slot(str, "QVariant", str)
    def unsubscribe(self, title, item, funcName):
        fKey = title + funcName
        if fKey not in self._funcDict:
            print(f"[Warning] qml取消订阅事件失败！fKey {fKey} 未在 __funcDict 中。")
            return
        func = self._funcDict[fKey]
        del self._funcDict[fKey]
        PubSubService.unsubscribe(title, func)

    # 取消订阅整个组的事件
    @Slot(str)
    def unsubscribeGroup(self, groupName):
        PubSubService.unsubscribeGroup(groupName)

    # 发布事件，在qml扩展此函数。传入 args 为参数列表。
    @Slot(str, list)
    def publish_(self, title, args):
        PubSubService.publish(title, *args)
