# 截图展示
from utils.config import Config
from utils.asset import Asset  # 资源
from ui.win_notify import Notify

import time
import tkinter as tk
from PIL import Image, ImageTk
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB
from io import BytesIO


class ShowImage:
    def __init__(self, imgData):
        self.imgData = imgData
        # 从位图数据创建PIL Image对象
        self.img = Image.open(BytesIO(imgData))
        self.ratio = self.img.width / self.img.height

        # 创建Tkinter窗口
        self.win = tk.Toplevel()
        self.win.iconphoto(False, Asset.getImgTK('umiocr24'))  # 设置窗口图标
        # 设置窗口大小
        self.w, self.h = self.img.width, self.img.height
        self.win.geometry(f'{self.w}x{self.h}')

        # 菜单栏
        self.menubar = tk.Menu(self.win)
        self.win.config(menu=self.menubar)
        self.menubar.add_command(label='　置顶', command=self.gotoTop)
        self.menubar.add_command(label='识别', command=self.ocr)
        self.menubar.add_command(label='保存', command=self.saveImage)
        # self.menubar.add_command(label='复制', command=self.copyImage)
        submenu = tk.Menu(self.menubar, tearoff=False)
        submenu.add_command(label='窗口置顶：Ctrl+T', command=self.gotoTop)
        submenu.add_command(label='文字识别：回车', command=self.ocr)
        submenu.add_command(label='保存图片到本地：Ctrl+S', command=self.saveImage)
        submenu.add_command(label='复制图片到剪贴板：Ctrl+C', command=self.copyImage)
        submenu.add_command(label='关闭窗口：Esc', command=self.onClose)
        self.menubar.add_cascade(label='更多', menu=submenu)

        # 创建Canvas对象并将其填充为整个窗口
        self.canvas = tk.Canvas(
            self.win, width=self.img.width, height=self.img.height)
        self.canvas.pack(fill='both', expand=True)
        self.photo = ImageTk.PhotoImage(self.img)  # 保存图片对象
        # 在Canvas上创建图像
        self.canvas_image = self.canvas.create_image(
            0, 0, anchor='nw', image=self.photo)
        # 隐藏Canvas的边框
        self.canvas.config(borderwidth=0, highlightthickness=0)

        # 绑定事件
        self.canvas.bind('<Configure>', self.onResize)  # 窗口大小改变事件
        self.win.bind('<Return>', self.ocr)
        self.win.bind('<Control-t>', self.gotoTop)
        self.win.bind('<Control-s>', self.saveImage)
        self.win.bind('<Control-c>', self.copyImage)
        self.win.bind('<Escape>', self.onClose)

        # 窗口属性
        self.isWindowTop = False
        if Config.get('isWindowTop'):  # 初始置顶
            self.gotoTop()
        self.win.after(200, lambda: self.win.focus())  # 窗口获得焦点

    def onResize(self, event):  # 缩放图像以适应Canvas的大小
        w, h = event.width, event.height
        imgW, imgH = w, h
        if w/h > self.ratio:  # 窗口更宽
            imgW = int(h*self.ratio)  # 重设图片宽度
        else:
            imgH = int(w/self.ratio)  # 重设图片高度
        resized_img = self.img.resize(
            (imgW, imgH), Image.ANTIALIAS)
        # 将PIL Image对象转换为Tkinter PhotoImage对象，并更新Canvas上的图像
        self.photo = ImageTk.PhotoImage(resized_img)
        self.canvas.itemconfigure(self.canvas_image, image=self.photo)
        self.w, self.h = w, h

    def gotoTop(self, event=None):
        self.isWindowTop = not self.isWindowTop
        if self.isWindowTop:  # 启用置顶
            self.menubar.entryconfigure(1, label='已置顶')
            self.win.attributes('-topmost', 1)
        else:
            self.menubar.entryconfigure(1, label='　置顶')
            self.win.attributes('-topmost', 0)

    def ocr(self, event=None):
        self.copyImage()
        Config.main.runClipboard()

    def saveImage(self, event=None):
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
            self.img.save(filePath, format='PNG')

    def copyImage(self, event=None):
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

    def onClose(self, event=None):
        self.photo = None  # 删除图片对象，释放内存
        self.win.destroy()  # 关闭窗口
