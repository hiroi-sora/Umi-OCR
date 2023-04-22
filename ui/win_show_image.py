# 截图展示
from utils.config import Config
from utils.asset import Asset  # 资源
from ui.win_notify import Notify

import time
import tkinter as tk
from PIL import Image, ImageTk
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB
from io import BytesIO

minSize = 140  # 最小大小


class ShowImage:
    def __init__(self, imgPIL=None, imgData=None, imgInfo=None):
        # imgPIL：PIL对象，imgData：位图数据。传入一个即可
        # imgInfo：图片信息，截图位置等。

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

        # 菜单栏
        self.menubar = tk.Menu(self.win)
        self.win.config(menu=self.menubar)
        self.menubar.add_command(label='锁定', command=self.__switchLock)
        self.menubar.add_command(label='识别', command=self.__ocr)
        self.menubar.add_command(label='保存', command=self.__saveImage)
        # self.menubar.add_command(label='复制', command=self.copyImage)
        submenu = tk.Menu(self.menubar, tearoff=False)
        submenu.add_command(label='锁定窗口+置顶：Ctrl+T 或 Ctrl+L',
                            command=lambda *e: self.__switchLock(1))
        submenu.add_command(label='文字识别：回车', command=self.__ocr)
        submenu.add_command(label='保存图片到本地：Ctrl+S', command=self.__saveImage)
        submenu.add_command(label='复制图片到剪贴板：Ctrl+C', command=self.__copyImage)
        submenu.add_command(label='关闭窗口：Esc', command=self.__onClose)
        self.menubar.add_cascade(label='更多', menu=submenu)

        # 创建Canvas对象并将其填充为整个窗口
        self.canvas = tk.Canvas(
            self.win, width=self.imgPIL.width, height=self.imgPIL.height)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.config(borderwidth=0, highlightthickness=0)  # 隐藏Canvas的边框
        # 在Canvas上创建图像
        self.imgCanvas = self.canvas.create_image(
            0, 0, anchor='nw', image=self.imgTK)

        # 缩放和移动相关参数
        imgArr = Asset.getImgTK('zoomArrow48')
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

        # 绑定事件
        self.win.bind('<Enter>', self.__onWinEnter)  # 鼠标进入窗口
        self.win.bind('<Leave>', self.__onWinLeave)  # 鼠标离开窗口
        self.canvas.bind('<ButtonPress-1>', self.__onCanvasPress)  # 按下画布
        self.canvas.bind('<ButtonRelease-1>', self.__onCanvasRelease)  # 松开画布
        self.canvas.bind('<B1-Motion>', self.__onCanvasMotion)  # 拖拽画布
        self.canvas.tag_bind(  # 鼠标进入缩放按钮
            self.zoomArrow1, '<Enter>', self.__onZoomEnter)
        self.canvas.tag_bind(  # 鼠标离开缩放按钮
            self.zoomArrow1, '<Leave>', self.__onZoomLeave)

        # 绑定快捷键
        self.win.bind('<Return>', self.__ocr)  # 回车：OCR
        self.win.bind(  # Ctrl+T：锁定&置顶
            '<Control-t>', lambda *e: self.__switchLock(0))
        self.win.bind(  # Ctrl+L：还是锁定&置顶
            '<Control-l>', lambda *e: self.__switchLock(0))
        self.win.bind('<Control-s>', self.__saveImage)  # Ctrl+S：保存
        self.win.bind('<Control-c>', self.__copyImage)  # Ctrl+C：复制图片
        self.win.bind('<Escape>', self.__onClose)  # Esc：关闭窗口

        # 窗口属性
        self.__resize(self.imgPIL.width, self.imgPIL.height)  # 设定初始大小
        self.isLock = False  # 初始值必为False

        # 初始处理
        def start():  # 展开
            self.win.attributes('-topmost', 1)  # 弹到最顶层
            if not Config.get('isWindowTop'):  # 跟随主窗口设置
                self.win.attributes('-topmost', 0)  # 取消锁定置顶
            self.win.focus()  # 窗口获得焦点
        self.win.after(200, start)

    def __resize(self, w, h):  # 缩放图片。应用w或h中按图片比例更大的一个值。
        # 适应w或h中比例更大的一个
        if w/h > self.ratio:
            h = int(w/self.ratio)  # w更大，则应用w，改变h
        else:
            w = int(h*self.ratio)  # h更大，则应用h，改变w
        # 防止窗口大小超出屏幕
        if w > self.win.winfo_screenwidth():
            w = self.win.winfo_screenwidth()
            h = int(w/self.ratio)
        if h > self.win.winfo_screenheight():
            h = self.win.winfo_screenheight()
            w = int(h*self.ratio)
        # 最小大小
        if w < minSize:
            w = minSize
            h = int(w/self.ratio)
        if h < minSize:
            h = minSize
            w = int(h*self.ratio)

        self.wh = (w, h)
        # 生成并设定缩放后的图片
        resizedImg = self.imgPIL.resize((w, h), Image.ANTIALIAS)
        self.imgTK = ImageTk.PhotoImage(resizedImg)
        self.canvas.itemconfigure(self.imgCanvas, image=self.imgTK)
        self.win.geometry(f'{w}x{h}')  # 缩放窗口
        # 移动缩放按钮
        ax, ay = w-self.zoomSize[0], h-self.zoomSize[1]
        self.canvas.coords(self.zoomArrow1, ax, ay)
        self.canvas.coords(self.zoomArrow2, ax, ay)

    # ============================== 事件 ==============================

    def __onWinEnter(self, e=None):  # 鼠标进入窗口
        if self.isLock:
            return
        self.canvas.itemconfig(self.zoomArrow1, state=tk.NORMAL)

    def __onWinLeave(self, e=None):  # 鼠标离开窗口
        self.canvas.itemconfig(self.zoomArrow1, state=tk.HIDDEN)

    def __canvasFunc(self, e, zoomFunc, moveFunc):  # 根据鼠标处于画布哪个位置，执行相应方法
        ids = self.canvas.find_withtag(tk.CURRENT)  # 获取当前鼠标位置的元素
        if self.zoomArrow1 in ids or self.zoomArrow2 in ids:  # 若是缩放按钮
            zoomFunc(e)
        else:  # 若是本体
            moveFunc(e)

    def __onCanvasPress(self, e=None):  # 按下画布
        self.__canvasFunc(e, zoomFunc=self.__onZoomPress,
                          moveFunc=self.__onMovePress)

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

    # ============================== 功能 ==============================

    def __switchLock(self, flag=0):  # 切换：锁定/解锁。
        # flag=0：切换。>0：锁定。<0：解锁。
        if flag == 0:
            self.isLock = not self.isLock
        elif flag > 0:
            self.isLock = True
        else:
            self.isLock = False

        if self.isLock:  # 启用锁定
            self.win.attributes('-topmost', 1)
        else:  # 解锁
            self.win.attributes('-topmost', 0)

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
