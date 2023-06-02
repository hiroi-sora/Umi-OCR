# =============================================
# =============== 页面控制器基类 ===============
# =============================================

from PySide2.QtCore import QObject


class Page(QObject):
    def __init__(self, objKey):
        super().__init__()
        self.objKey = objKey
        print(f"py控制器 {self.objKey} 实例化！")

    def __del__(self):
        print(f"py控制器 {self.objKey} 销毁！")
