# msn == Mission
# 任务器的基类。引擎执行一次流水线 __runMission 时，会调用任务器的方法

import tkinter as tk
import tkinter.messagebox

from utils.logger import GetLog
Log = GetLog()


class Msn:

    def onStart(self, num):
        Log.info(f'Msn onStart 未定义！\nnum: {num}')

    def onGet(self, num, data):
        Log.info(f'Msn onGet 未定义！\nnum: {num}\ndata: {data}')

    def onStop(self):
        Log.info(f'Msn onStop 未定义！')

    def onError(self, err):
        tk.messagebox.showerror(
            '遇到了亿点小问题',
            f'任务失败：{err}')
