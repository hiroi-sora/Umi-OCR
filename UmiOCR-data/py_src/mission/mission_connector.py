# =====================================================================
# =============== qml与【后端Python任务控制器们】的连接器 ===============
# =====================================================================

from PySide2.QtCore import QObject, Slot, Signal

# 本模块内定义的任务控制器单例
from .mission_ocr import MissionOCR

# 控制器字典
MsnObjDict = {"ocr": MissionOCR}


# 任务连接器类（不限制单例）
class MissionConnector(QObject):
    # qml访问某个Python任务控制器的方法（同步）
    # qml调用ctrlKey的方法funcName，入参为列表（对应参数顺序），返回值为可变类型。
    @Slot(str, str, list, result="QVariant")
    def callPy(self, msnKey, funcName, args=()):
        if msnKey not in MsnObjDict:
            print(f"【Error】任务连接器：qml访问不存在的任务控制器{msnKey}")
            return None
        # 获取方法的引用
        msnObj = MsnObjDict[msnKey]
        method = getattr(msnObj, funcName, None)
        # 查询失败
        if not callable(method):
            print(f"【Error】任务连接器：qml调用了{msnKey}的不存在的py方法{funcName}！")
            return None
        # 调用方法，参数不对的话让系统抛出错误
        return method(*args)
