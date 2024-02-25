# ===========================================================================
# =============== 【前端qml标签页】与【后端Python控制器】的连接器 ===============
# ===========================================================================

"""
每一个qml页面，都可以拥有一个对应的Python控制器实例。
前端页面访问各种后端功能，必须靠这个控制器作为中转。
"""

from PySide2.QtCore import QObject, Slot

# 导入本模块内定义的控制器类
from .BatchOCR import BatchOCR
from .BatchDOC import BatchDOC
from .ScreenshotOCR import ScreenshotOCR
from .QRcode import QRcode
from ..utils.call_func import CallFunc

# 控制器类列表
PageClass = [BatchOCR, ScreenshotOCR, QRcode, BatchDOC]


TagPageConnObj = None  # 记录实例
# PySide2 没有 qmlRegisterSingletonType，PyQt5或者PySide6中才有。
# 不过没关系，我们手动维护控制器的单例状态就是了


# 页面连接器类（手动单例）
class TagPageConnector(QObject):
    def __init__(self):
        global TagPageConnObj
        # 1. 检查是否单例
        if not TagPageConnObj == None:
            raise Exception("【Error】TagPageConnector只允许创建一个实例！")
        TagPageConnObj = self
        super().__init__()
        # 2. 收集所有已导入的控制器类，聚集为dict。   ["类名"]=类
        self.pageClass = {}
        for i in PageClass:
            self.pageClass[i.__name__] = i
        # 属性
        # 当前已实例化的控制器
        self.pages = {}
        self._keysNum = {}  # 记录每个key被生成了多少次

    # ========================= 【增删改查】 =========================

    # 增： 新增一个class为key的控制器，返回这个控制器的标识符。失败返回空字符串
    @Slot(str, result=str)
    def addPage(self, key):
        if key not in self.pageClass:
            return ""
        ctrlKey = self._getCtrlKey(key)
        obj = self.pageClass[key](ctrlKey, self)  # 实例化 页控制器对象
        self.pages[ctrlKey] = {  # key为控制器id
            "pyObj": obj,  # py对象
            "qmlObj": None,  # qml对象
            "pyCache": {},  # py方法缓存
            "qmlCache": {},  # qml方法缓存
        }
        return ctrlKey

    # 增： 新增一个不带控制器的简单页
    @Slot(str, result=str)
    def addSimplePage(self, key):
        ctrlKey = self._getCtrlKey(key)
        self.pages[ctrlKey] = {
            "pyObj": None,
            "qmlObj": None,
            "pyCache": {},
            "qmlCache": {},
        }
        return ctrlKey

    # 增2： qml回调，设置标识符为ctrlKey的控制器，对应的qml页面对象
    @Slot(str, "QVariant")
    def setPageQmlObj(self, ctrlKey, qmlObj):
        if ctrlKey not in self.pages:
            return False
        self.pages[ctrlKey]["qmlObj"] = qmlObj

    # 删： 删除标识符为ctrlKey的控制器。成功返回true
    @Slot(str, result=bool)
    def delPage(self, ctrlKey):
        if ctrlKey not in self.pages:
            return False
        del self.pages[ctrlKey]
        return True

    # ========================= 【与qml的通信】 =========================

    # qml调用Python的方法（同步）
    # qml调用ctrlKey的方法funcName，入参为列表（对应参数顺序），返回值为可变类型。
    @Slot(str, str, list, result="QVariant")
    def callPy(self, ctrlKey, funcName, args):
        if ctrlKey not in self.pages:
            print(f"【Warning】调用py方法{funcName}，但{ctrlKey}不存在！")
            return None
        page = self.pages[ctrlKey]
        # 获取方法的引用
        method = None
        if funcName in page["pyCache"]:  # 缓存中存在，直接取缓存
            method = page["pyCache"][funcName]
        else:  # 否则，搜索该方法，并写入缓存
            method = getattr(page["pyObj"], funcName, None)
            page["pyCache"][funcName] = method
        # 查询失败
        if not method:
            print(f"【Error】调用了{ctrlKey}的不存在的py方法{funcName}！")
            return None
        # 调用方法，参数不对的话让系统抛出错误
        return method(*args)

    # python调用qml的函数（同步）
    def callQml(self, ctrlKey, funcName, *args):
        if ctrlKey not in self.pages:
            print(f"【Warning】调用qml方法{funcName}，但{ctrlKey}不存在！")
            return None
        page = self.pages[ctrlKey]
        # 获取方法的引用
        method = None
        if funcName in page["qmlCache"]:  # 缓存中存在，直接取缓存
            method = page["qmlCache"][funcName]
        else:  # 否则，搜索该方法，并写入缓存
            method = getattr(page["qmlObj"], funcName, None)
            page["qmlCache"][funcName] = method
        # 查询失败
        if not method:
            print(f"【Error】调用了{ctrlKey}的不存在的qml方法{funcName}！")
            return None
        # 调用方法，参数不对的话让系统抛出错误
        return method(*args)

    # 在子线程中调用，到主线程中调用python函数
    def callFunc(self, func, *args):
        CallFunc.now(func, *args)

    # ==================================================

    # 生成一个ctrlKey
    def _getCtrlKey(self, key):
        if key not in self._keysNum:
            n = 1
        else:
            n = self._keysNum[key] + 1
        self._keysNum[key] = n
        return f"{key}_{n}"
