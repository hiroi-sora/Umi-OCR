# msn == Mission

import tkinter as tk
import time


class Msn:

    def onStart(self, num):
        print(f'Msn onStart 未定义！\nnum: {num}')

    def onGet(self, num, data):
        print(f'Msn onGet 未定义！\nnum: {num}\ndata: {data}')

    def onStop(self):
        print(f'Msn onStop 未定义！')

    def onError(self, err):
        tk.messagebox.showerror(
            '遇到了亿点小问题',
            f'识别器初始化失败：{err}\n\n请检查配置有无问题！')
