# ===================================================================
# =============== 前端qml标签页的后端Python控制器的管理 ===============
# ===================================================================

"""
每一个qml页面，都可以拥有一个对应的Python控制器实例。
前端页面访问各种后端功能，必须靠这个控制器作为中转。
"""

from PySide2.QtCore import QObject, Slot, Property

# 导入本模块内定义的控制器类
from .BatchOCR import BatchOCR

# 控制器类列表
PageClass = [
    BatchOCR
]


SingObj = None  # 记录实例
# PySide2 没有 qmlRegisterSingletonType，PyQt5或者PySide6中才有。
# 不过没关系，我们手动维护控制器的单例状态就是了


# 页面控制器类（手动单例）
class TagPageController(QObject):

    def __init__(self):
        global SingObj
        # 1. 检查是否单例
        if not SingObj == None:
            raise Exception("【Error】TagPageController只允许创建一个实例！")
        SingObj = self
        super().__init__()
        # 2. 收集所有已导入的控制器类，聚集为dict。   ["类名"]=类
        self.pageClass = {}
        for i in PageClass:
            self.pageClass[i.__name__] = i
        # 属性
        self.page = {}  # 当前已实例化的控制器。每一项为：{obj:对象, funcCache:{方法缓存字典}}
        self.keyIndex = 0  # 用于生成标识符

    # ========================= 【增删改查】 =========================

    # 增： 新增一个class为key的控制器，返回这个控制器的标识符。失败返回空字符串
    @Slot(str, result=str)
    def addPage(self, key):
        if key not in self.pageClass:
            return ""
        self.keyIndex += 1
        objKey = f"{self.pageClass[key].__name__}_{self.keyIndex}"
        obj = self.pageClass[key](objKey)  # 实例化 页控制器对象
        self.page[objKey] = {"obj": obj, "funcCache": {}}
        return objKey

    # 删： 删除标识符为objKey的控制器。成功返回true
    @Slot(str, result=bool)
    def delPage(self, objKey):
        if objKey not in self.page:
            return False
        del self.page[objKey]
        return True

    # ========================= 【与qml的通信】 =========================

    # qml调用Python方法：
    # qml调用objKey的方法funcName，入参为列表（对应参数顺序），返回值为可变类型。
    @Slot(str, str, list, result="QVariant")
    def call(self, objKey, funcName, args):
        page = self.page[objKey]
        # 获取方法的引用
        method = None
        if funcName in page["funcCache"]:  # 缓存中存在，直接取缓存
            method = page["funcCache"][funcName]
        else:  # 否则，搜索该方法，并写入缓存
            method = getattr(page["obj"], funcName, None)
            page["funcCache"][funcName] = method
        # 查询失败
        if not method:
            print(f"【Error】调用了{objKey}的不存在的方法{funcName}！")
            return None
        # 调用方法，参数不对的话让系统抛出错误
        return method(*args)
