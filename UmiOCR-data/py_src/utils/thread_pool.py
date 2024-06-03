# =====================================================
# =============== 全局线程池 异步任务接口 ===============
# =====================================================

import traceback
from PySide2.QtCore import QThreadPool, QRunnable

# 全局线程池
GlobalThreadPool = QThreadPool.globalInstance()


# 异步类
class Runnable(QRunnable):
    def __init__(self, taskFunc, *args, **kwargs):
        super().__init__()
        self._taskFunc = taskFunc
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            self._taskFunc(*self._args, **self._kwargs)
        except Exception as e:
            err = traceback.format_exc()
            print(f"[Error] 异步运行发生错误: {err}")


# 启动异步类
def threadPoolStart(runnable: QRunnable):
    # 检查线程池是否满，并扩充
    activeThreadCount = GlobalThreadPool.activeThreadCount()
    if activeThreadCount >= GlobalThreadPool.maxThreadCount():
        print(f"[Warning] 线程池已满 {activeThreadCount} ！自动扩充+1。")
        GlobalThreadPool.setMaxThreadCount(activeThreadCount + 1)
    GlobalThreadPool.start(runnable)


# 快捷接口：异步运行函数，返回异步类的对象
def threadRun(taskFunc, *args, **kwargs):
    runnable = Runnable(taskFunc, *args, **kwargs)
    threadPoolStart(runnable)
    return runnable
