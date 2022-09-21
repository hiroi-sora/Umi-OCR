from win32.win32api import EnumDisplayMonitors  # 获取显示器信息
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB  # 剪贴板
from io import BytesIO

import tkinter as tk
from PIL import ImageGrab, ImageTk
from enum import Enum
import keyboard  # 绑定快捷键


class _DrawMode(Enum):
    ready = 1  # 准备中
    drag = 2  # 拖拽中


class ScreenshotWin():
    OB = -10  # 元素隐藏屏幕外的位置

    def __init__(self, closeSendData=None):
        self.closeSendData = closeSendData  # 向父窗口发送数据的接口
        # “虚拟屏幕”指多显示器画面的拼凑在一起的完整画面
        self.image = ImageGrab.grab(all_screens=True)  # 对整个虚拟屏幕截图，物理分辨率
        self.imageResult = None  # 结果图片
        # 创建窗口
        self.topwin = tk.Toplevel()
        self.topwin.withdraw()  # 初始化期间隐藏截图窗
        self.topwin.overrideredirect(True)  # 无边框
        # self.topwin.attributes('-topmost', 1)  # 设置层级最前 TODO
        self.debugEle = []  # 调试信息画布元素
        self.flashEle = []  # 闪光元素
        self.drawMode = _DrawMode.ready  # 准备模式
        # 获取所有屏幕的信息，提取其中的坐标信息(虚拟，非物理分辨率)
        scInfos = EnumDisplayMonitors()  # 所有屏幕的信息
        self.scBoxList = [s[2] for s in scInfos]  # 提取虚拟分辨率的信息
        # 计算虚拟屏幕最左上角和最右下角的坐标
        scUp, scDown, scLeft, scRight = 0, 0, 0, 0
        for s in self.scBoxList:  # 遍历所有屏幕，获取最值
            if s[0] < scLeft:  # 左边缘
                scLeft = s[0]
            if s[1] < scUp:  # 上边缘
                scUp = s[1]
            if s[2] > scRight:  # 右边缘
                scRight = s[2]
            if s[3] > scDown:  # 下边缘
                scDown = s[3]
        # 计算虚拟屏幕的宽和高
        scWidth, scHeight = scRight - scLeft, scDown - scUp
        self.scBoxVirtual = (scLeft, scUp, scRight, scDown,
                             scWidth, scHeight)
        self.scScale = self.image.size[0] / scWidth  # 缩放比例
        # 主窗口设置为铺满虚拟屏幕
        bd, bdp = 2, 1  # 边缘要额外拓展1像素，以免无法接收到鼠标在边缘的点击
        scStr = f'{scWidth+bd}x{scHeight+bd}+{scLeft-bdp}+{scUp-bdp}'
        self.topwin.geometry(scStr)
        # 创建画布，铺满主窗
        self.canvas = tk.Canvas(self.topwin, width=scWidth+bd, height=scHeight+bd,
                                highlightthickness=0, borderwidth=0,  # 取消边框
                                cursor='plus', bg=None)
        self.canvas.pack(fill='both')
        # 原图改物理为虚拟屏幕分辨率，转成tk格式，导入画布
        self.imageTK = ImageTk.PhotoImage(
            self.image.resize((scWidth, scHeight)))

        # 初始化所有画布元素
        self.canvas.create_image(  # 底图
            bdp, bdp, anchor='nw', image=self.imageTK)
        rec1 = self.canvas.create_rectangle(
            self.OB, self.OB, self.OB, self.OB, outline='white', width=2)  # 实线底层
        rec2 = self.canvas.create_rectangle(  # 虚线表层
            self.OB, self.OB, self.OB, self.OB, outline='black', width=2, dash=10)
        self.sightBox = (rec1, rec2)  # 瞄准盒
        self.sightBoxXY = [self.OB, self.OB, self.OB, self.OB]  # 瞄准盒坐标
        lineW = self.canvas.create_line(self.OB, self.OB, self.OB, self.OB,
                                        fill='green', width=1)
        lineH = self.canvas.create_line(self.OB, self.OB, self.OB, self.OB,
                                        fill='green', width=1)
        self.sightLine = (lineW, lineH)  # 瞄准线
        # TODO : demo
        # self.topwin.configure(bg='black')
        # self.topwin.attributes("-alpha", 0.8)  # 透明

        # 绑定事件
        # self.canvas.bind('<KeyPress-Escape>', self.__onClose)  # 绑定Esc退出
        # self.canvas.bind('<Control-Shift-Alt-KeyPress-D>',
        #                  self.__switchDebug)  # 调试信息
        keyboard.add_hotkey('Esc', self.__onClose, suppress=False)  # 绑定Esc退出
        keyboard.add_hotkey('Ctrl+Shift+Alt+D',
                            self.__switchDebug, suppress=False)  # 调试信息
        # 画布绑定鼠标事件
        for i in ('1', '2', '3'):  # 绑定左中右三个鼠标键
            self.canvas.bind(f'<Button-{i}>', self.__onDown)  # 按下
            self.canvas.bind(f'<ButtonRelease-{i}>', self.__onUp)  # 松开
        self.canvas.bind('<Motion>', self.__onMotion)  # 鼠标移动
        self.canvas.bind('<Enter>', self.__onMotion)  # 鼠标进入，用于初始化瞄准线

        self.topwin.deiconify()  # 初始化完毕，显示截图窗
        self.__flash()
        # self.topwin.mainloop()

    def __onDown(self, event):  # 鼠标按下
        if self.drawMode == _DrawMode.ready:  # 进入拖拽模式
            self.drawMode = _DrawMode.drag
            # 记录起始点
            self.sightBoxXY[0], self.sightBoxXY[1] = event.x, event.y
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            # 隐藏瞄准线
            for i in (0, 1):
                self.canvas.coords(
                    self.sightLine[i], self.OB, self.OB, self.OB, self.OB)
        elif self.drawMode == _DrawMode.drag:  # 若已在拖拽中，按下另一个鼠标键
            self.drawMode = _DrawMode.ready  # 退出拖拽模式
            self.sightBoxXY = [self.OB, self.OB, self.OB, self.OB]
            for i in (0, 1):  # 隐藏瞄准盒，显示瞄准线
                self.canvas.coords(
                    self.sightBox[i], self.OB, self.OB, self.OB, self.OB)
            self.canvas.coords(self.sightLine[0],
                               0, event.y, self.scBoxVirtual[4], event.y)
            self.canvas.coords(self.sightLine[1],
                               event.x, 0, event.x, self.scBoxVirtual[5])

    def __onUp(self, event):  # 鼠标松开
        if self.drawMode == _DrawMode.drag:  # 离开拖拽模式
            self.drawMode = _DrawMode.ready
            # 记录结束点
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            self.__onClose()

    def __onMotion(self, event):  # 鼠标移动
        if self.drawMode == _DrawMode.ready:  # 准备模式，刷新瞄准线
            self.canvas.coords(self.sightLine[0],
                               0, event.y, self.scBoxVirtual[4], event.y)
            self.canvas.coords(self.sightLine[1],
                               event.x, 0, event.x, self.scBoxVirtual[5])
        elif self.drawMode == _DrawMode.drag:  # 拖拽模式，刷新瞄准盒
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            for i in (0, 1):
                self.canvas.coords(self.sightBox[i],
                                   self.sightBoxXY[0], self.sightBoxXY[1], event.x, event.y)

    def __onClose(self, event=None):  # 关闭窗口
        box = self.sightBoxXY
        if box[0] < 0 and box[1] < 0 and box[2] < 0 and box[3] < 0:
            pass  # 未截图
        elif box[0] == box[2] or box[1] == box[3]:
            pass  # 截图面积为0，无效
        else:
            if box[0] > box[2]:  # 若坐标错位（第二点不在第一点右下角）则交换
                box[0], box[2] = box[2], box[0]
            if box[1] > box[3]:
                box[1], box[3] = box[3], box[1]
            for i in range(4):
                box[i] *= self.scScale  # 乘上缩放比例
            self.imageResult = self.image.crop(box)
        self.topwin.destroy()  # 销毁窗口
        # 解绑快捷键
        keyboard.remove_hotkey('Esc')
        keyboard.remove_hotkey('Ctrl+Shift+Alt+D')
        if self.closeSendData:
            flag = self.copyImage()
            self.closeSendData(flag)

    def __flash(self):  # 边缘闪光，提示已截图
        color = 'white'
        width = 100

        def closeFlash():  # 关闭闪光
            for i in self.flashEle:
                self.canvas.delete(i)
            self.flashEle = []
        for box in self.scBoxList:
            p1x, p1y, p2x, p2y = box
            p1x -= self.scBoxVirtual[0]
            p2x -= self.scBoxVirtual[0]
            p1y -= self.scBoxVirtual[1]
            p2y -= self.scBoxVirtual[1]
            e = self.canvas.create_rectangle(
                p1x, p1y, p2x, p2y, outline=color, width=width)
            self.flashEle.append(e)
        self.topwin.after(200, closeFlash)

    def __switchDebug(self, event=None):  # 切换显示/隐藏调试信息
        color = 'red'
        if self.debugEle:  # 删除调试信息
            for i in self.debugEle:
                self.canvas.delete(i)
            self.debugEle = []
        else:  # 创建调试信息
            for index, box in enumerate(self.scBoxList):
                p1x, p1y, p2x, p2y = box
                p1x -= self.scBoxVirtual[0]
                p2x -= self.scBoxVirtual[0]
                p1y -= self.scBoxVirtual[1]
                p2y -= self.scBoxVirtual[1]
                e = self.canvas.create_rectangle(
                    p1x, p1y, p2x, p2y, outline=color, width=3)
                self.debugEle.append(e)
                e = self.canvas.create_line(
                    p1x, p1y, p2x, p2y, fill=color, width=3)
                self.debugEle.append(e)
                e = self.canvas.create_line(
                    p2x, p1y, p1x, p2y, fill=color, width=3)
                self.debugEle.append(e)
                # 文字提示框
                e = self.canvas.create_rectangle(
                    p1x+10, p1y+10, p1x+340, p1y+60, fill='white', width=0)
                self.debugEle.append(e)
                e = self.canvas.create_text(p1x+15, p1y+15,
                                            font=('', 15, 'bold'), fill=color, anchor='nw',
                                            text=f'屏幕{index+1}: {box}')
                self.debugEle.append(e)
                e = self.canvas.create_text(p1x+15, p1y+43,
                                            font=('', 10, ''), fill=color, anchor='nw',
                                            text=f'按 Ctrl+Shift+Alt+D 关闭调试信息')
                self.debugEle.append(e)

    def getImage(self):
        '''获取截图。若失败或退出，则返回None'''
        return self.imageResult

    def copyImage(self):
        '''复制截图到剪贴板。成功返回True，否则False'''
        if not self.imageResult:
            return False
        # 图片转字节
        output = BytesIO()
        self.imageResult.save(output, 'BMP')  # 以位图保存
        imgData = output.getvalue()[14:]  # 去除header
        output.close()
        # 写入剪贴板
        OpenClipboard()  # 打开剪贴板
        EmptyClipboard()  # 清空剪贴板
        SetClipboardData(CF_DIB, imgData)  # 写入
        CloseClipboard()  # 关闭
        return True
