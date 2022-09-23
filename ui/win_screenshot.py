from utils.logger import GetLog
from utils.config import Config

from win32.win32api import EnumDisplayMonitors  # 获取显示器信息
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB  # 剪贴板
from io import BytesIO

import tkinter as tk
from PIL import ImageGrab, ImageTk
from enum import Enum
import keyboard  # 绑定快捷键

Log = GetLog()


class _DrawMode(Enum):
    ready = 1  # 准备中
    drag = 2  # 拖拽中


class ScreenshotWin():
    OB = -10  # 元素隐藏屏幕外的位置

    def __init__(self):
        self.isInitWin = False  # 防止重复初始化窗体
        self.isInitGrab = False  # 防止未初始化截图参数时触发事件

    def initWin(self):  # 初始化窗体
        self.isInitWin = True
        # 创建窗口
        self.topwin = tk.Toplevel()
        self.topwin.withdraw()  # 隐藏窗口
        self.topwin.overrideredirect(True)  # 无边框
        self.topwin.configure(bg='black')
        self.topwin.attributes("-alpha", 0.8)  # 透明
        self.topwin.attributes('-topmost', 1)  # 设置层级最前 TODO
        self.closeSendData = Config.main.closeScreenshot  # 向父窗口发送数据的接口
        # 创建画布及画布元素。后创建的层级在上。
        self.canvas = tk.Canvas(self.topwin, cursor='plus', bg=None,
                                highlightthickness=0, borderwidth=0)  # 取消边框
        self.canvas.pack(fill='both')
        # 瞄准盒
        rec1 = self.canvas.create_rectangle(  # 实线底层
            self.OB, self.OB, self.OB, self.OB, outline='white', width=2)
        rec2 = self.canvas.create_rectangle(  # 虚线表层
            self.OB, self.OB, self.OB, self.OB, outline='black', width=2, dash=10)
        self.sightBox = (rec1, rec2)
        self.sightBoxXY = [self.OB, self.OB, self.OB, self.OB]  # 瞄准盒坐标
        # 瞄准线
        lineW = self.canvas.create_line(  # 纵向
            self.OB, self.OB, self.OB, self.OB, fill='green', width=1)
        lineH = self.canvas.create_line(  # 横向
            self.OB, self.OB, self.OB, self.OB, fill='green', width=1)
        self.sightLine = (lineW, lineH)
        # debug模块
        self.debugXYBox = self.canvas.create_rectangle(  # 坐标下面的底
            self.OB, self.OB, self.OB, self.OB, fill='yellow', outline='#999', width=1)
        self.debugXYText = self.canvas.create_text(self.OB, self.OB,  # 显示坐标
                                                   font=('Microsoft YaHei', 15, 'bold'), fill='red', anchor='nw')
        self.debugList = []  # 显示屏幕信息
        # 闪光模块
        self.flashList = []  # 闪光元素
        # 绑定全局事件
        keyboard.add_hotkey('Esc', self.__onClose,   # 绑定Esc退出
                            suppress=False, timeout=1)
        keyboard.add_hotkey('Ctrl+Shift+Alt+D', self.__switchDebug,  # 切换调试信息
                            suppress=False, timeout=0)
        # 绑定画布事件
        self.canvas.bind(f'<Button-1>', self.__onDown)  # 左键按下
        self.canvas.bind(f'<Button-3>', self.__repaint)  # 右键按下
        self.canvas.bind(f'<ButtonRelease-1>', self.__onUp)  # 左键松开
        self.canvas.bind('<Motion>', self.__onMotion)  # 鼠标移动
        self.canvas.bind('<Enter>', self.__onMotion)  # 鼠标进入，用于初始化瞄准线
        Log.info('初始化截图窗口')

    def initGrab(self):  # 初始化截屏
        # “虚拟屏幕”指多显示器画面的拼凑在一起的完整画面
        self.image = ImageGrab.grab(all_screens=True)  # 对整个虚拟屏幕截图，物理分辨率

        if not self.isInitWin:
            self.initWin()

        self.imageResult = None  # 结果图片
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
        self.canvas['width'] = scWidth+bd
        self.canvas['height'] = scHeight+bd
        # 原图改物理为虚拟屏幕分辨率，转成tk格式，导入画布
        self.imageTK = ImageTk.PhotoImage(
            self.image.resize((scWidth, scHeight)))
        cimg = self.canvas.create_image(  # 底图
            bdp, bdp, anchor='nw', image=self.imageTK)
        self.canvas.lower(cimg)  # 移动到最下方

        self.topwin.deiconify()  # 显示窗口
        self.isInitGrab = True
        Log.info('初始化截图')
        for index, box in enumerate(self.scBoxList):
            Log.info(f'屏幕{index}: {box} {box[2]-box[0]} {box[3]-box[1]}')
        Log.info(f'虚拟屏幕：{self.scBoxVirtual}')
        if Config.get('isOutputDebug') and not self.debugList:
            self.__switchDebug()
        self.__flash()  # 闪光

    def __hideElement(self, ele, size=4):  # 隐藏一个画布元素
        # 实际上是挪到画布外
        if size == 2:
            self.canvas.coords(ele, self.OB, self.OB)
        elif size == 4:
            self.canvas.coords(ele, self.OB, self.OB, self.OB, self.OB)

    def __onDown(self, event):  # 鼠标按下
        Log.info('左键按下')
        if self.drawMode == _DrawMode.ready:  # 进入拖拽模式
            self.drawMode = _DrawMode.drag
            # 记录起始点
            self.sightBoxXY[0], self.sightBoxXY[1] = event.x, event.y
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            # 隐藏瞄准线
            for i in (0, 1):
                self.__hideElement(self.sightLine[i], 4)

    def __onUp(self, event):  # 鼠标松开
        Log.info('左键抬起')
        if self.drawMode == _DrawMode.drag:  # 离开拖拽模式
            self.drawMode = _DrawMode.ready
            # 记录结束点
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            self.__createGrabImg()  # 生成剪切图像
            self.__onClose()  # 关闭窗口

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
        if self.debugList:
            self.canvas.coords(self.debugXYText, event.x+6, event.y+3)
            self.canvas.coords(self.debugXYBox, event.x+3,
                               event.y+3, event.x+130, event.y+28)
            self.canvas.itemconfig(self.debugXYText, {'text':
                                                      f'{event.x} , {event.y}'})

    def __repaint(self, event):  # 重绘
        Log.info('重绘')
        if self.drawMode == _DrawMode.drag:  # 已在拖拽中
            self.drawMode = _DrawMode.ready  # 退出拖拽模式
            self.sightBoxXY = [self.OB, self.OB, self.OB, self.OB]
            for i in (0, 1):  # 隐藏瞄准盒，显示瞄准线
                self.__hideElement(self.sightBox[i], 4)
            self.canvas.coords(self.sightLine[0],
                               0, event.y, self.scBoxVirtual[4], event.y)
            self.canvas.coords(self.sightLine[1],
                               event.x, 0, event.x, self.scBoxVirtual[5])
        elif self.drawMode == _DrawMode.ready:  # 还在准备中
            self.__onClose()  # 关闭

    def __createGrabImg(self):  # 创建剪切图像
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

    def __onClose(self, event=None):  # 关闭窗口
        if not self.isInitGrab:
            return
        Log.info('关闭截图')
        self.topwin.withdraw()  # 隐藏窗口
        # 隐藏元素
        for i in (0, 1):
            self.__hideElement(self.sightBox[i])
            self.__hideElement(self.sightLine[i])
        #  初始化参数
        self.isInitGrab = False
        self.drawMode = _DrawMode.ready
        if self.closeSendData:
            flag = self.copyImage()  # 复制图像
            self.image = None  # 删除图像
            self.imageResult = None  # 删除
            self.closeSendData(flag)

    def __flash(self):  # 边缘闪光，提示已截图
        color = 'white'
        width = 100

        def closeFlash():  # 关闭闪光
            for i in self.flashList:
                self.canvas.delete(i)
            self.flashList = []
        for box in self.scBoxList:
            p1x, p1y, p2x, p2y = box
            p1x -= self.scBoxVirtual[0]
            p2x -= self.scBoxVirtual[0]
            p1y -= self.scBoxVirtual[1]
            p2y -= self.scBoxVirtual[1]
            e = self.canvas.create_rectangle(
                p1x, p1y, p2x, p2y, outline=color, width=width)
            self.flashList.append(e)
        self.topwin.after(200, closeFlash)

    def __switchDebug(self, event=None):  # 切换显示/隐藏调试信息
        if not self.isInitGrab:
            return
        print('__switchDebug')
        color = 'red'
        if self.debugList:  # 删除调试信息
            for i in self.debugList:
                self.canvas.delete(i)
            self.debugList = []
            self.__hideElement(self.debugXYBox, 4)
            self.__hideElement(self.debugXYText, 2)
        else:  # 创建调试信息
            for index, box in enumerate(self.scBoxList):
                p1x, p1y, p2x, p2y = box
                p1x -= self.scBoxVirtual[0]
                p2x -= self.scBoxVirtual[0]
                p1y -= self.scBoxVirtual[1]
                p2y -= self.scBoxVirtual[1]
                e = self.canvas.create_rectangle(
                    p1x, p1y, p2x, p2y, outline=color, width=3)
                self.debugList.append(e)
                e = self.canvas.create_line(
                    p1x, p1y, p2x, p2y, fill=color, width=3)
                self.debugList.append(e)
                e = self.canvas.create_line(
                    p2x, p1y, p1x, p2y, fill=color, width=3)
                self.debugList.append(e)
                # 文字提示框
                e = self.canvas.create_rectangle(
                    p1x+10, p1y+10, p1x+440, p1y+60, fill='white', width=0)
                self.debugList.append(e)
                e = self.canvas.create_text(p1x+15, p1y+15,
                                            font=('', 15, 'bold'), fill=color, anchor='nw',
                                            text=f'屏幕{index+1}: {box} | {box[2]-box[0]},{box[3]-box[1]}')
                self.debugList.append(e)
                e = self.canvas.create_text(p1x+15, p1y+43,
                                            font=('', 10, ''), fill=color, anchor='nw',
                                            text=f'按 Ctrl+Shift+Alt+D 关闭调试信息')
                self.debugList.append(e)
            self.canvas.lift(self.debugXYBox)  # 移动到最上方
            self.canvas.lift(self.debugXYText)  # 移动到最上方

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
        try:
            OpenClipboard()  # 打开剪贴板
            EmptyClipboard()  # 清空剪贴板
            SetClipboardData(CF_DIB, imgData)  # 写入
            CloseClipboard()  # 关闭
        except Exception as err:
            tk.messagebox.showerror(
                '遇到了一点小问题',
                f'截图写入剪贴板失败，请检测是否有其他程序正在占用。\n{err}')
        return True


SSW = ScreenshotWin()
