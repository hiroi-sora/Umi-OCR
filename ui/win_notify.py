from utils.config import Config

import tkinter as tk
from enum import Enum

winW, winH = 300, 60  # 宽高
winR = 15  # 圆角半径
winPosY = 60  # 窗口与屏幕下方的距离
xxS1 = 14  # 叉叉进度条大小（直径）
xxS2 = 10  # 叉叉进度条离右上角的距离
bgColor = '#FFCBE0'  # 背景色
teS1 = 12  # 主标题字号
teS2 = 9  # 次内容字号
teP1 = (12, 9)  # 主标题位置
teP2 = (12, 35)  # 次内容位置
popTime = 0.4  # 弹出动画时长，秒
downTime = 6  # 自动关闭倒计时时长，秒
frameTime = 30  # 动画帧间隔，毫秒
winR2 = winR*2


class State(Enum):
    none = 0  # 无
    starting = 1  # 弹出中
    showing = 2  # 显示中


class NotifyWindow():
    def __init__(self):
        self.win = None
        self.state = State.none
        self.afters = [None, None, None]  # 保存运行中的计时器

    def __initWin(self):  # 初始化窗体
        self.win = tk.Toplevel()
        self.win.withdraw()
        self.win.attributes('-alpha', 0)  # 透明度

        self.__winGO()  # 初始化窗口位置
        self.win.resizable(False, False)  # 锁定大小
        self.win.overrideredirect(True)  # 无边框模式
        self.win['bg'] = '#FFFFFF'
        self.win.attributes('-transparentcolor', '#FFFFFF')  # 设置纯白色为透明
        # 画布
        self.canvas = tk.Canvas(self.win, bg='#FFFFFF', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.__onClick)
        # 绘制圆角矩形
        self.canvas.create_oval(
            0, 0, winR2, winR2, fill=bgColor, outline='')
        self.canvas.create_oval(
            winW-winR2, 0, winW, winR2, fill=bgColor, outline='')
        self.canvas.create_oval(
            winW-winR2, winH-winR2, winW, winH, fill=bgColor, outline='')
        self.canvas.create_oval(
            0, winH-winR2, winR2, winH, fill=bgColor, outline='')
        self.canvas.create_rectangle(
            winR, 0, winW-winR, winH, fill=bgColor, outline='')
        self.canvas.create_rectangle(
            0, winR, winW, winH-winR, fill=bgColor, outline='')
        # 绘制叉叉进度条
        self.prog = self.canvas.create_arc(winW-xxS1-xxS2, xxS2, winW-xxS2, xxS1+xxS2,
                                           fill='', outline='gray', width=1, style='arc',
                                           start=90, extent=0)
        # self.canvas.create_text(
        #     winW-xxS2-int(xxS1/2), xxS2+int(xxS1/2), anchor='center',
        #     font=('Microsoft YaHei', xxS1-xxS2), text='×')
        # 绘制文本
        self.text1 = self.canvas.create_text(
            *teP1, anchor='nw', font=('Microsoft YaHei', teS1),
            text='')
        self.text2 = self.canvas.create_text(
            *teP2, anchor='nw', font=('Microsoft YaHei', teS2), fill='#666',
            text='')

    @staticmethod
    def __easing(i):  # 0-1之间的缓动函数，越靠近0增长越快
        return 1+(i-1)*(i-1)*(i-1)

    def __winGO(self, yValue=0):  # 移动窗口
        winX = int((self.win.winfo_screenwidth() - winW) / 2)  # 位置：屏幕中下
        winY = int(self.win.winfo_screenheight() - winH - yValue)
        self.win.geometry(f'{winW}x{winH}+{winX}+{winY}')

    def __actionStart(self, t=popTime):  # 开始弹alpha出动画
        if t <= 0:
            self.state = State.showing  # 状态：显示中
            return
        p = (popTime-t)/popTime  # 0→1
        p = self.__easing(p)  # 缓动
        y = winPosY * p
        self.__winGO(y)  # 移动窗口
        self.win.attributes('-alpha', p)  # 透明度
        self.afters[0] = self.win.after(
            frameTime, lambda: self.__actionStart(t-frameTime/1000))

    def __actionEnd(self, t=popTime):  # 结束弹回动画
        if t <= 0:
            self.close()
            return
        p = t/popTime  # 1→0
        p = self.__easing(p)  # 缓动
        y = winPosY * p
        self.__winGO(y)  # 移动窗口
        self.win.attributes('-alpha', p)  # 透明度
        self.afters[1] = self.win.after(
            frameTime, lambda: self.__actionEnd(t-frameTime/1000))

    def __actionCountdown(self, t=downTime):  # 倒计时动画
        if t <= 0:
            self.__actionEnd()
            return
        extent = 360 * (t/downTime)  # 360→0
        if extent < 5:
            extent = 0
        self.canvas.itemconfig(self.prog, extent=extent)
        self.afters[2] = self.win.after(
            frameTime, lambda: self.__actionCountdown(t-frameTime/1000))

    def __onClick(self, *e):  # 点击事件
        self.__afterCancel()  # 取消所有运行中的计时器
        self.canvas.itemconfig(self.prog, extent=0)  # 倒计时复位
        self.__actionEnd()  # 动画关闭

    def __afterCancel(self):  # 取消所有运行中的计时器
        for i, a in enumerate(self.afters):
            if a:
                self.win.after_cancel(a)
                self.afters[i] = None

    def show(self, title, message):
        '''显示一条消息。'''
        if not self.win:
            self.__initWin()
        if not self.state == State.none:
            self.close()  # 关闭上一条消息
        self.state = State.starting  # 状态：弹出中
        # 初始化参数
        self.__winGO()  # 位置
        self.win.attributes('-alpha', 0)  # 透明度
        self.canvas.itemconfig(self.prog, extent=0)  # 进度条
        # 修改文字
        title = title.replace('\n', '')
        message = message.replace('\n', '')
        self.canvas.itemconfig(self.text1, text=title)
        self.canvas.itemconfig(self.text2, text=message)
        # 恢复窗口
        self.win.attributes('-topmost', 1)  # 设置层级最前
        self.win.state('normal')  # 恢复前台状态
        # 弹出动画
        self.__actionStart()
        # 启动倒计时动画
        if downTime > 0:
            self.__actionCountdown()

    def close(self):
        '''关闭当前通知'''
        if self.state == State.none:
            return
        self.win.withdraw()  # 隐藏消息
        self.__afterCancel()  # 取消所有运行中的计时器
        self.state = State.none


NotifyWin = NotifyWindow()


def Notify(title, msg):
    if not Config.get('isNotify'):
        return
    NotifyWin.show(title, msg)


def NotifyClose():
    NotifyWin.close()
