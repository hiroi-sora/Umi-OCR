# ==========================================
# =============== OCR组件基类 ===============
# ==========================================

from PySide2 import QtCore


class OCR():

    def __init__(self):
        self.__missions = ['rest'] # 任务列表
        self.__msnMutex = QtCore.QMutex() # 任务列表的锁
        self.__msnThread = None # 任务线程
        print('OCR模块初始化完毕。')

    def add(self, mission):
        """添加一个或多个异步OCR任务\n
        `mission` 为单个字典或字典列表：\n
        {
        选填一项\n
            "path":      "图片路径，字符串",\n
            "bytes":     图片字节流,\n
            "base64":    "图片编码Base64字符串",\n
            "clipboard": None 标记为剪贴板任务，值留空,\n
        必填\n
            "callback":  回调函数
        }
        """
        if isinstance(mission, dict):
            mission = [mission]
        if not isinstance(mission, list):
            raise ValueError("mission 类型错误，必须为字典或列表")
        
        self.__msnMutex.lock()  # 上锁
        for m in mission:
            # TODO: 检测参数合法性
            self.__msnMutex.append(m)
        self.__msnMutex.unlock()  # 解锁