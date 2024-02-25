# =============================================
# =============== 简单任务管理器 ===============
# =============================================


from PySide2.QtCore import QMutex, QThreadPool, QRunnable


class SimpleMission:
    def __init__(self, msnTask):
        self._msnTask = msnTask  # 任务函数
        self._msnList = []  # 任务队列
        self._msnMutex = QMutex()  # 任务队列的锁
        self._task = None  # 异步任务对象
        self._taskMutex = QMutex()  # 任务对象的锁
        self._threadPool = QThreadPool.globalInstance()  # 全局线程池

    def addMissionList(self, msnList):  # 添加一条任务队列，返回任务ID
        if len(msnList) < 1:
            return "[Error] len(msnList) < 1 !"
        # 添加到任务队列
        self._msnMutex.lock()  # 上锁
        self._msnList += msnList
        self._msnMutex.unlock()  # 解锁
        # 启动任务
        self._startMsns()
        return "[Success]"

    def _startMsns(self):  # 启动异步任务，执行所有任务列表
        # 若当前异步任务对象为空，则创建工作线程
        self._taskMutex.lock()  # 上锁
        if self._task == None:
            self._task = self._Task(self._taskRun)
            self._threadPool.start(self._task)
        self._taskMutex.unlock()  # 解锁

    # ========================= 【子线程 方法】 =========================

    def _taskRun(self):  # 异步执行任务字典的流程
        # 循环，直到任务队列的列表为空
        while True:
            self._msnMutex.lock()  # 上锁
            dl = len(self._msnList)  # 任务字典长度
            if dl == 0:  # 任务队列已空
                self._msnMutex.unlock()  # 解锁
                break
            msn = self._msnList.pop(0)  # 取一个任务
            self._msnMutex.unlock()  # 解锁
            if callable(self._msnTask):
                self._msnTask(msn)
        # 完成
        self._taskFinish()

    def _taskFinish(self):  # 任务结束
        self._taskMutex.lock()  # 上锁
        self._task = None
        self._taskMutex.unlock()  # 解锁

    # ========================= 【异步类】 =========================

    class _Task(QRunnable):
        def __init__(self, taskFunc):
            super().__init__()
            self._taskFunc = taskFunc

        def run(self):
            self._taskFunc()
