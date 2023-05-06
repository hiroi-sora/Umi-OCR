# 截图展示
from utils.config import Config
from utils.asset import Asset  # 资源
from ui.win_notify import Notify
from utils.hotkey import Hotkey

import time
import tkinter as tk
from PIL import Image, ImageTk
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB
from io import BytesIO

MinSize = 140  # 最小大小
MaxSizeMargin = 80  # 最大大小时，距离屏幕边缘的空隙
RatioThreshold = 3  # 当图片长宽比例大于该阈值时，缩放操作只读取鼠标的纵/横向移动，以避免短边缩放过快。


class ShowImage:
    def __init__(self, imgPIL=None, imgData=None, title='', initPos=None):
        # imgPIL：PIL对象，imgData：位图数据。必须传入任意一个或两个。
        # title：窗口标题（可选）
        # initPos：窗口初始位置（可选），4位列表：[左上x，左上y，宽w，高h]

        # 初始化图片数据
        self.imgPIL, self.imgData = imgPIL, imgData
        if not self.imgData and not self.imgPIL:
            return
        if not self.imgData:  # 从PIL Image对象创建位图数据
            output = BytesIO()
            imgPIL.save(output, 'BMP')  # 以位图保存
            self.imgData = output.getvalue()[14:]  # 去除header
            output.close()
        if not self.imgPIL:  # 从位图数据创建PIL Image对象
            self.imgPIL = Image.open(BytesIO(imgData))
        self.imgTK = ImageTk.PhotoImage(self.imgPIL)  # 保存图片对象
        self.ratio = self.imgPIL.width / self.imgPIL.height  # 图片比例
        self.wh = (self.imgPIL.width, self.imgPIL.height)  # 当前图片宽高

        # 创建Tkinter窗口
        self.win = tk.Toplevel()
        self.win.iconphoto(False, Asset.getImgTK('umiocr24'))  # 设置窗口图标
        self.win.resizable(False, False)  # 禁止原生缩放窗口
        if not title:  # 创建标题
            title = f'预览 {time.strftime("%H:%M")} （{self.wh[0]}x{self.wh[1]}）'
        self.win.title(title)

        # 菜单栏
        self.menubar = tk.Menu(self.win)
        self.win.config(menu=self.menubar)
        self.menubar.add_command(label='锁定', command=self.__switchLock)
        self.menubar.add_command(label='识别', command=self.__ocr)
        self.menubar.add_command(label='保存', command=self.__saveImage)
        # self.menubar.add_command(label='复制', command=self.copyImage)
        submenu = tk.Menu(self.menubar, tearoff=False)
        submenu.add_command(label='锁定窗口：Ctrl+T 或 Ctrl+L',
                            command=lambda *e: self.__switchLock(1))
        submenu.add_command(label='文字识别：回车', command=self.__ocr)
        submenu.add_command(label='保存图片到本地：Ctrl+S', command=self.__saveImage)
        submenu.add_command(label='复制图片到剪贴板：Ctrl+C', command=self.__copyImage)
        submenu.add_command(label='关闭窗口：Esc', command=self.__onClose)
        submenu.add_command(label='移动窗口：拖拽任意位置')
        submenu.add_command(label='缩放窗口：拖拽右下角箭头图标')
        submenu.add_command(label='缩放窗口：鼠标滚轮')
        submenu.add_command(label='调整透明度：Ctrl+滚轮')
        self.menubar.add_cascade(label='更多', menu=submenu)

        # 创建Canvas对象并将其填充为整个窗口
        self.canvas = tk.Canvas(
            self.win, width=self.imgPIL.width, height=self.imgPIL.height, relief='solid')
        self.canvas.pack(fill='both', expand=True)
        self.canvas.config(borderwidth=0, highlightthickness=0)  # 隐藏Canvas的边框
        # 在Canvas上创建图像
        self.imgCanvas = self.canvas.create_image(
            0, 0, anchor='nw', image=self.imgTK)

        # 缩放和移动相关参数
        imgArr = Asset.getImgTK('zoomArrowAlpha48')
        self.zoomSize = (imgArr.width(), imgArr.height())
        self.mouseOriginXY = None  # 本次操作的起始鼠标位置
        self.zoomOriginWH = None  # 本次缩放的起始图片宽高
        self.zoomArrow2 = self.canvas.create_image(  # 缩放箭头第2层（鼠标进入时显示）
            self.wh[0]-self.zoomSize[0], self.wh[1]-self.zoomSize[1], anchor='nw', image=imgArr)
        self.zoomArrow1 = self.canvas.create_image(  # 缩放箭头第1层（鼠标接近时显示）
            self.wh[0]-self.zoomSize[0], self.wh[1]-self.zoomSize[1], anchor='nw', image=imgArr)
        self.canvas.itemconfig(self.zoomArrow1, state=tk.HIDDEN)  # 默认隐藏1、2层
        self.canvas.itemconfig(self.zoomArrow2, state=tk.HIDDEN)
        self.moveOriginXY = None  # 本次移动的起始窗口位置

        # 锁定相关
        imgLock = Asset.getImgTK('lockAlpha48')
        self.isLock = False  # 初始值必为False
        self.lockX, self.lockY = 0, 0  # 锁定模式下的窗口偏移量
        self.lockBtn2 = self.canvas.create_image(  # 锁定图标第2层（鼠标进入时显示）
            0, 0, anchor='nw', image=imgLock)
        self.lockBtn1 = self.canvas.create_image(  # 锁定图标第1层（鼠标接近时显示）
            0, 0, anchor='nw', image=imgLock)
        self.canvas.itemconfig(self.lockBtn1, state=tk.HIDDEN)  # 默认隐藏1、2层
        self.canvas.itemconfig(self.lockBtn2, state=tk.HIDDEN)

        # 绑定事件
        self.win.bind('<Enter>', self.__onWinEnter)  # 鼠标进入窗口
        self.win.bind('<Leave>', self.__onWinLeave)  # 鼠标离开窗口
        self.canvas.bind('<ButtonPress-1>', self.__onCanvasPress)  # 按下画布
        self.canvas.bind('<ButtonRelease-1>', self.__onCanvasRelease)  # 松开画布
        self.canvas.bind('<B1-Motion>', self.__onCanvasMotion)  # 拖拽画布
        self.canvas.bind('<MouseWheel>', self.__onMouseWheel)  # 滚轮缩放或透明度调整
        # 鼠标进入和离开缩放按钮
        self.canvas.tag_bind(self.zoomArrow1, '<Enter>', self.__onZoomEnter)
        self.canvas.tag_bind(self.zoomArrow1, '<Leave>', self.__onZoomLeave)
        # 鼠标进入、离开锁定按钮
        self.canvas.tag_bind(self.lockBtn1, '<Enter>', self.__onLockEnter)
        self.canvas.tag_bind(self.lockBtn1, '<Leave>', self.__onLockLeave)

        # 绑定快捷键
        self.win.bind('<Return>', self.__ocr)  # 回车：OCR
        self.win.bind('<Control-s>', self.__saveImage)  # Ctrl+S：保存
        self.win.bind('<Control-c>', self.__copyImage)  # Ctrl+C：复制图片
        self.win.bind('<Escape>', self.__onClose)  # Esc：关闭窗口
        # Ctrl+T 和 ctrl+L：锁定&置顶
        self.win.bind('<Control-t>', lambda *e: self.__switchLock(0))
        self.win.bind('<Control-l>', lambda *e: self.__switchLock(0))

        # 初始处理
        def start():  # 展开
            self.win.attributes('-topmost', 1)  # 弹到最顶层
            if not Config.get('isWindowTop'):  # 跟随主窗口设置
                self.win.attributes('-topmost', 0)  # 取消锁定置顶
            self.win.focus()  # 窗口获得焦点
        self.win.after(200, start)
        # 设定初始大小和位置
        if initPos:  # 已设定初始值
            x, y, w, h = initPos  # 解包元组
        else:  # 未设定初始值，则由鼠标位置决定
            x, y = Hotkey.getMousePos()  # 获取鼠标位置
            w, h = self.wh[0], self.wh[1]  # 窗口大小=图像长宽
            x, y = x-w//2, y-h//2  # 窗口中心移到鼠标位置
        self.win.geometry(f'+{x}+{y}')  # 设定初始位置
        self.win.update()  # 必须先update一下再设定大小，否则菜单栏的高度会被吃掉
        self.__resize(w, h)  # 设定初始大小

    # ============================== 事件 ==============================

    def __onWinEnter(self, e=None):  # 鼠标进入窗口
        if self.isLock:  # 锁定状态：显示解锁图标
            self.canvas.itemconfig(self.lockBtn1, state=tk.NORMAL)
        else:  # 非锁定状态：显示缩放图标
            self.canvas.itemconfig(self.zoomArrow1, state=tk.NORMAL)

    def __onWinLeave(self, e=None):  # 鼠标离开窗口
        self.canvas.itemconfig(self.zoomArrow1, state=tk.HIDDEN)
        self.canvas.itemconfig(self.lockBtn1, state=tk.HIDDEN)

    def __canvasFunc(self, e, zoomFunc, moveFunc, lockFunc=None):  # 根据鼠标处于画布哪个位置，执行相应方法
        ids = self.canvas.find_withtag(tk.CURRENT)  # 获取当前鼠标位置的元素
        if self.zoomArrow1 in ids:  # 若是缩放按钮
            zoomFunc(e)
        elif self.lockBtn1 in ids and lockFunc:  # 若是锁定按钮
            lockFunc(e)
        else:  # 若是本体
            moveFunc(e)

    def __onCanvasPress(self, e=None):  # 按下画布
        self.__canvasFunc(e, zoomFunc=self.__onZoomPress,
                          moveFunc=self.__onMovePress,
                          lockFunc=self.__onClickUnlock)

    def __onCanvasRelease(self, e=None):  # 松开画布
        self.__canvasFunc(e, zoomFunc=self.__onZoomRelease,
                          moveFunc=self.__onMoveRelease)

    def __onCanvasMotion(self, e=None):  # 拖拽画布
        if self.isLock:
            return
        self.__canvasFunc(e, zoomFunc=self.__onZoomMotion,
                          moveFunc=self.__onMoveMotion)

    def __onZoomEnter(self, e=None):  # 鼠标进入缩放按钮
        if self.isLock:
            return
        self.canvas.itemconfig(self.zoomArrow2, state=tk.NORMAL)  # 显示2层图标
        self.canvas.config(cursor='sizing')  # 改变光标为缩放箭头

    def __onZoomLeave(self, e=None):  # 鼠标离开缩放按钮
        self.canvas.itemconfig(self.zoomArrow2, state=tk.HIDDEN)
        self.canvas.config(cursor='')  # 改变光标为正常

    def __onZoomPress(self, e=None):  # 按下缩放按钮
        self.mouseOriginXY = (e.x_root, e.y_root)
        self.zoomOriginWH = self.wh  # 读取宽高起点

    def __onZoomRelease(self, e=None):  # 松开缩放按钮
        self.mouseOriginXY = None

    def __onZoomMotion(self, e=None):  # 拖拽缩放按钮
        if self.isLock:
            return
        dx = e.x_root-self.mouseOriginXY[0]  # 离原点的移动量
        dy = e.y_root-self.mouseOriginXY[1]
        nw, nh = self.zoomOriginWH[0]+dx, self.zoomOriginWH[1]+dy  # 计算大小设定
        if self.ratio > RatioThreshold:  # 图像 w 过大，忽视鼠标竖向移动
            nh = 0
        elif self.ratio < 1/RatioThreshold:  # 图像 h 过大，忽视鼠标横向移动
            nw = 0
        self.__resize(nw, nh)  # 重置图片大小

    def __onMovePress(self, e=None):  # 按下移动区域
        self.mouseOriginXY = (e.x_root, e.y_root)  # 必须用_root，排除窗口相对移动的干扰
        self.moveOriginXY = (self.win.winfo_x(), self.win.winfo_y())

    def __onMoveRelease(self, e=None):  # 松开移动区域
        self.mouseOriginXY = None
        self.moveOriginXY = None

    def __onMoveMotion(self, e=None):  # 拖拽移动区域
        if self.isLock:
            return
        dx = e.x_root-self.mouseOriginXY[0]  # 离原点的移动量
        dy = e.y_root-self.mouseOriginXY[1]
        nx, ny = self.moveOriginXY[0]+dx, self.moveOriginXY[1]+dy  # 计算位置设定
        self.win.geometry(f'+{nx}+{ny}')  # 移动窗口

    def __onLockEnter(self, e=None):  # 进入解锁按钮
        if not self.isLock:
            return
        self.canvas.itemconfig(self.lockBtn2, state=tk.NORMAL)  # 显示2层图标
        self.canvas.config(cursor='hand2')  # 改变光标为手指

    def __onLockLeave(self, e=None):  # 离开解锁按钮
        self.canvas.itemconfig(self.lockBtn2, state=tk.HIDDEN)
        self.canvas.config(cursor='')  # 改变光标为正常

    def __onClickUnlock(self, e=None):  # 单击解锁
        self.__switchLock(-1)

    def __onMouseWheel(self, e=None):  # 滚轮
        if self.isLock:
            return
        if e.state == 0:  # 什么都不按，缩放
            step = 30
            s = step if e.delta > 0 else -step
            w = self.wh[0]+s
            self.__resize(w, 0)
        else:  # 按下任何修饰键（Ctrl、Shift等），调整透明度
            step = 0.1
            s = step if e.delta > 0 else -step
            alpha = self.win.attributes('-alpha')
            a = alpha+s
            if a < 0.3:
                a = 0.3
            if a > 1:
                a = 1
            self.win.attributes('-alpha', a)

    # ============================== 功能 ==============================

    def __resize(self, w, h):  # 重设图片和窗口大小。应用w或h中按图片比例更大的一个值。
        if h <= 0:  # 防止除零
            h = 1
        # 适应w或h中比例更大的一个
        if w/h > self.ratio:
            h = int(w/self.ratio)  # w更大，则应用w，改变h
        else:
            w = int(h*self.ratio)  # h更大，则应用h，改变w
        # 防止窗口大小超出屏幕
        if w > self.win.winfo_screenwidth()-MaxSizeMargin:
            w = self.win.winfo_screenwidth()-MaxSizeMargin
            h = int(w/self.ratio)
        if h > self.win.winfo_screenheight()-MaxSizeMargin:
            h = self.win.winfo_screenheight()-MaxSizeMargin
            w = int(h*self.ratio)
        # 最小大小
        if w < MinSize and h < MinSize:
            if self.ratio > 1:  # 图像宽更大，则防止窗口宽度过小
                w = MinSize
                h = int(w/self.ratio)
            else:  # 高同理
                h = MinSize
                w = int(h*self.ratio)

        self.wh = (w, h)
        # 生成并设定缩放后的图片
        resizedImg = self.imgPIL.resize((w, h), Image.BILINEAR)
        self.imgTK = ImageTk.PhotoImage(resizedImg)
        self.canvas.itemconfigure(self.imgCanvas, image=self.imgTK)
        self.win.geometry(f'{w}x{h}')  # 缩放窗口
        # 移动缩放按钮
        ax, ay = w-self.zoomSize[0], h-self.zoomSize[1]
        self.canvas.coords(self.zoomArrow1, ax, ay)
        self.canvas.coords(self.zoomArrow2, ax, ay)

    def __switchLock(self, flag=0):  # 切换：锁定/解锁。
        # flag=0：切换。>0：锁定。<0：解锁。
        if flag == 0:
            self.isLock = not self.isLock
        elif flag > 0:
            self.isLock = True
        else:
            self.isLock = False

        winx, winy = self.win.winfo_x(), self.win.winfo_y()  # 当前相对位置
        self.__onWinLeave()
        if self.isLock:  # 启用锁定
            rootx, rooty = self.win.winfo_rootx(), self.win.winfo_rooty()  # 原本的绝对位置
            self.win.attributes('-topmost', 1)  # 窗口置顶
            self.win.config(menu='')  # 移除菜单栏
            self.win.overrideredirect(True)  # 将窗口设置为无边框模式
            self.canvas.config(borderwidth=1)  # 添加画布边框
            self.win.update()  # 刷新一下
            # 移动窗口，补偿菜单和边框消失的偏移
            self.lockX, self.lockY = self.win.winfo_rootx()-rootx, self.win.winfo_rooty()-rooty
            self.win.geometry(f'+{winx-self.lockX}+{winy-self.lockY}')
        else:  # 解锁
            self.canvas.itemconfig(self.zoomArrow1, state=tk.NORMAL)
            self.win.attributes('-topmost', 0)  # 取消置顶
            self.win.config(menu=self.menubar)  # 恢复菜单栏
            self.win.overrideredirect(False)  # 取消无边框模式
            self.canvas.config(borderwidth=0)  # 取消画布边框
            self.win.update()  # 刷新一下
            # 移动窗口，补偿菜单和边框恢复的偏移
            self.win.geometry(f'+{winx+self.lockX}+{winy+self.lockY}')

    def __ocr(self, e=None):
        self.__copyImage()
        Config.main.runClipboard()

    def __saveImage(self, e=None):
        # 打开文件选择对话框
        now = time.strftime("%Y-%m-%d %H%M%S", time.localtime())
        defaultFileName = f'屏幕截图 {now}.png'
        filePath = tk.filedialog.asksaveasfilename(
            initialfile=defaultFileName,
            defaultextension='.png',
            filetypes=[('PNG Image', '*.png')],
            title='保存图片'
        )

        if filePath:
            # 将 PIL.Image 对象保存为 PNG 文件
            self.imgPIL.save(filePath, format='PNG')

    def __copyImage(self, e=None):
        try:
            OpenClipboard()  # 打开剪贴板
            EmptyClipboard()  # 清空剪贴板
            SetClipboardData(CF_DIB, self.imgData)  # 写入
        except Exception as err:
            Notify('位图无法写入剪贴板', f'{err}')
        finally:
            try:
                CloseClipboard()  # 关闭
            except Exception as err:
                Notify('无法关闭剪贴板', f'{err}')

    def __onClose(self, e=None):
        self.imgTK = None  # 删除图片对象，释放内存
        self.win.destroy()  # 关闭窗口
