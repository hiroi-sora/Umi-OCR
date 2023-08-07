# ========================================================
# =============== 发布/订阅连接器，在qml调用 ===============
# ========================================================

from PySide2.QtCore import QObject, Slot

from .pubsub_service import PubSubService


class PubSubConnector(QObject):
    # 订阅事件。传入 标题，函数所在Item，函数名
    @Slot(str, "QVariant", str)
    def subscribe(self, title, item, funcName):
        func = getattr(item, funcName, None)
        if not func:
            print(f"[Error] qml订阅事件失败！未在 {item} 中找到函数 {funcName} 。")
            return
        PubSubService.subscribe(title, func)

    # 取消订阅事件
    @Slot(str, "QVariant", str)
    def unsubscribe(self, title, item, funcName):
        func = getattr(item, funcName, None)
        if not func:
            print(f"[Error] qml取消订阅事件失败！未在 {item} 中找到函数 {funcName} 。")
            return
        PubSubService.unsubscribe(title, func)

    # 发布事件，在qml扩展此函数。传入 args 为参数列表。
    @Slot(str, list)
    def publish_(self, title, args):
        PubSubService.publish(title, *args)
