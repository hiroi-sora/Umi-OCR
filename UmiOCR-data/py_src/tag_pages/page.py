# =============================================
# =============== 页面控制器基类 ===============
# =============================================

from PySide2.QtCore import QObject


class Page(QObject):
    def __init__(self, ctrlKey, controller):
        super().__init__()
        self.ctrlKey = ctrlKey
        self.controller = controller
        print(f"py控制器 {self.ctrlKey} 实例化！")

    def __del__(self):
        print(f"py控制器 {self.ctrlKey} 销毁！")

    def callQml(self, funcName, *args):  # python调用qml函数
        return self.controller.callQml(self.ctrlKey, funcName, *args)

    def callQmlInMain(self, funcName, *args):  # python调用qml函数，可在子线程调用
        self.callFunc(self.callQml, funcName, *args)

    def callFunc(self, func, *args):  # 在主线程中调用py函数
        return self.controller.callFunc(func, *args)

    def getQmlValueDict(self):  # python获取qml配置字典
        return self.controller.callQml(self.ctrlKey, "getValueDict").toVariant()

    def getQmlOriginDict(self):
        return self.controller.callQml(self.ctrlKey, "getOriginDict").toVariant()

    def setQmlValue(self, key, val):  # python获取qml配置字典
        return self.controller.callQml(self.ctrlKey, "setValue", key, val).toVariant()
