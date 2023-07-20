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
        return self.controller.callQmlInMain(self.ctrlKey, funcName, *args)

    def getQmlConfigValueDict(self):  # python获取qml配置字典
        return self.controller.callQml(self.ctrlKey, "getConfigValueDict").toVariant()
