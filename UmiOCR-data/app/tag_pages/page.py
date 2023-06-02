# =============================================
# =============== 页面控制器基类 ===============
# =============================================


class Page:
    def __init__(self, objKey):
        self.objKey = objKey
        print(f"py控制器 {self.objKey} 实例化！")

    def __del__(self):
        print(f"py控制器 {self.objKey} 销毁！")
