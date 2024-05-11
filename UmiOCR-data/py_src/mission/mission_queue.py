# 任务队列类

from uuid import uuid4
from typing import Callable, Any


class MissionQueue:
    def __init__(
        self,
        msnList: list,  # 任务内容列表，每项为一个任务元素
        configs: dict = {},  # 任务控制参数
        # 回调函数
        # 整个队列 即将启动。回调参数(self)
        onStart: Callable[["MissionQueue"], None] = None,
        # 单个任务 准备进行。回调参数(self, 任务元素)
        onReady: Callable[["MissionQueue", Any], None] = None,
        # 单个任务 完成。回调参数(self, 任务元素, 任务结果)
        onGet: Callable[["MissionQueue"], None] = None,
        # 整个队列 已结束。回调参数(self, 结果标志)
        # 结果标志："[Success]...", "[Warning]...", "[Error]..."
        onEnd: Callable[["MissionQueue", str], None] = None,
    ):
        self.msnList = msnList
        self.configs = configs
        self.id = str(uuid4())  # 任务ID
        self.len = len(msnList)  # 队列总长度
        self.index = 0  # 当前任务下标
        self._onStart = onStart if onStart else self._pass
        self._onReady = onReady if onReady else self._pass
        self._onGet = onGet if onGet else self._pass
        self._onEnd = onEnd if onEnd else self._pass
        # 工作状态： "waiting" "running"
        self.state_work = "waiting"
        # 控制状态： "" "pause" "stop"
        self.state_ctrl = ""

    # ==================== mission调用 ====================

    # 获取剩余任务长度
    def remainingLen(self):
        return self.len - self.index

    # 判空 【1】←在一轮任务循环中的调用顺序
    def empty(self):
        return self.index >= self.len

    # 获取一个任务元素 【2】
    def getMsn(self):
        return self.msnList[self.index]

    # 完成一个任务元素 【4】
    def popMsn(self):
        self.index += 1

    # 恢复进行
    def resume(self):
        if self.state_ctrl == "pause":
            self.state_ctrl = ""

    # 暂停
    def pause(self):
        self.state_ctrl = "pause"

    # 停止（废弃）
    def stop(self):
        self.state_ctrl = "stop"

    # ==================== 回调函数 ====================

    def onStart(self):
        try:
            self._onStart(self)
        except Exception as e:
            print(f"[Error] onStart: {e}")

    def onReady(self):  #  【3】
        try:
            self._onReady(self)
        except Exception as e:
            print(f"[Error] onReady: {e}")

    def onGet(self, res):  #  【4】
        try:
            self._onGet(self, res)
        except Exception as e:
            print(f"[Error] onGet: {e}")

    def onEnd(self, flag):
        # 结果标志："[Success]...", "[Warning]...", "[Error]..."
        try:
            self._onEnd(self, flag)
        except Exception as e:
            print(f"[Error] onEnd: {e}")

    @staticmethod
    def _pass(*e):  # 空函数
        pass
