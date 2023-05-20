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
        self.page = {}  # 当前已实例化的控制器。
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
        self.page[objKey] = obj
        return objKey

    # 删： 删除标识符为objKey的控制器。成功返回true
    @Slot(str, result=bool)
    def delPage(self, objKey):
        if objKey not in self.page:
            return False
        del self.page[objKey]
        return True

    @Slot(int, int, result=int)
    def hello(self, a=1, b=2):
        print("调用了hello")
        return 3

    @Slot(list, result=list)
    def helloList(self, a):
        print("传入列表", a)
        return ["666", "返回列表"]

    @Slot("QVariant", result="QVariant")
    def helloDict(self, a):
        print("传入属性", dir(a))
        print("解析", a.toVariant())
        return {"aaa": "字典", "bbb": "第二个参数"}
