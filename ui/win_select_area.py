from ocr.engine import OCRe  # 引擎单例
from utils.asset import Asset  # 资源
from utils.config import Config
from ui.widget import Widget  # 控件

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from windnd import hook_dropfiles  # 文件拖拽
from PIL import Image, ImageTk
import os


class IgnoreAreaWin:
    def __init__(self, closeSendData=None, defaultPath=""):
        self.closeSendData = closeSendData  # 向父窗口发送数据的接口
        self.balloon = Config.main.balloon  # 气泡框
        self.cW = 960  # 画板尺寸
        self.cH = 540
        self.tran = 2  # 绘制偏移量
        self.areaColor = ["red", "green",  # 各个矩形区域的标志颜色
                          "darkorange", "white"]

        # def initWin():  # 初始化主窗口
        # 主窗口
        self.win = tk.Toplevel()
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)
        self.win.title("选择区域")
        self.win.resizable(False, False)  # 禁止窗口拉伸
        # 变量初始化
        self.imgSize = (-1, -1)  # 图像尺寸，初次加载时生效。
        self.imgScale = -1  # 图片缩放比例
        self.imgSizeText = tk.StringVar(value="未设定")
        self.area = [[], [], []]  # 存储各个矩形区域的列表
        self.areaHistory = []  # 绘图历史，撤销用
        self.areaTextRec = []  # 文字区域提示框
        self.areaType = -1  # 当前绘图模式
        self.areaTypeIndex = [-1, -1, -1]  # 当前绘制的矩形的序号
        self.lastPath = ''  # 上一次导入的图片的路径
        # 图标
        self.win.iconphoto(False, Asset.getImgTK('umiocr24'))  # 设置窗口图标
        # initWin()

        # def initPanel():  # 初始化面板
        tk.Frame(self.win, height=10).pack(side='top')
        ctrlFrame = tk.Frame(self.win)
        ctrlFrame.pack(side='top', fill='y')
        ctrlF0 = tk.Frame(ctrlFrame)
        ctrlF0.pack(side='left')
        tk.Label(ctrlF0, text="【图像分辨率】").pack()
        tk.Label(ctrlF0, textvariable=self.imgSizeText).pack()
        tk.Label(ctrlF0, text="不符合该分辨率的图片\n忽略区域设置不会生效",
                 fg='gray', wraplength=120).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        # 复选框
        ctrlF1 = tk.Frame(ctrlFrame)
        ctrlF1.pack(side='left')
        self.isAutoOCR = tk.BooleanVar()
        self.isAutoOCR.set(True)
        wid = ttk.Checkbutton(
            ctrlF1, variable=self.isAutoOCR, text='启用 OCR结果预览')
        wid.grid(column=0, row=0, sticky='w')
        self.balloon.bind(wid, '以虚线框标出OCR识别到的文本块')
        wid = ttk.Checkbutton(
            ctrlF1, variable=Config.getTK('isAreaWinAutoTbpu'), text='启用 文块后处理预览')
        Config.addTrace('isAreaWinAutoTbpu', self.reLoadImage)
        wid.grid(column=0, row=1, sticky='w')
        self.balloon.bind(
            wid, '以虚线框标出经过文本块后处理的块\n注意，仅用于预览后处理效果，\n实际任务时忽略区域早于后处理执行，不受后处理的影响')
        Widget.comboboxFrame(ctrlF1, '', 'tbpu', width=18).grid(
            column=0, row=2, sticky='w')
        # 切换画笔按钮
        tk.Frame(ctrlFrame, w=30).pack(side='left')
        ctrlF2 = tk.Frame(ctrlFrame)
        ctrlF2.pack(side='left')
        self.buttons = [None, None, None]
        btnW = 15
        self.buttons[0] = tk.Button(ctrlF2, text='+忽略区域 A', width=btnW, height=3, fg=self.areaColor[0], bg=self.areaColor[3],
                                    command=lambda: self.changeMode(0))
        self.buttons[0].pack(side='left', padx=5)
        self.balloon.bind(
            self.buttons[0], '处于 [忽略区域 A] 内的矩形虚线文字块将被忽略\n一般情况下，将需要去除的水印区域全部画上区域A即可')
        tk.Frame(ctrlFrame, w=20).pack(side='left')
        self.buttons[1] = tk.Button(ctrlF2, text='+识别区域', width=btnW, height=3, fg=self.areaColor[1], bg=self.areaColor[3],
                                    command=lambda: self.changeMode(1))
        self.buttons[1].pack(side='left', padx=5)
        self.balloon.bind(
            self.buttons[1], '若 [识别区域] 内存在文字块，则 [忽略区域 A] 失效')
        tk.Frame(ctrlFrame, w=20).pack(side='left')
        self.buttons[2] = tk.Button(ctrlF2, text='+忽略区域 B', width=btnW, height=3, fg=self.areaColor[2], bg=self.areaColor[3],
                                    command=lambda: self.changeMode(2))
        self.buttons[2].pack(side='left', padx=5)
        self.balloon.bind(
            self.buttons[2], '当 [忽略区域 A] 失效，即触发 [识别区域] 时，\n[忽略区域 B] 生效')

        tk.Frame(ctrlFrame, w=20).pack(side='left')
        ctrlF4 = tk.Frame(ctrlFrame)
        ctrlF4.pack(side='left')
        tk.Button(ctrlF4, text='清空', width=12, bg='white',
                  command=self.clearCanvas).pack()
        tk.Button(ctrlF4, text='撤销\nCtrl+Shift+Z', width=12, bg='white',
                  command=self.revokeCanvas).pack(pady=5)
        self.win.bind("<Control-Z>", self.revokeCanvas)  # 绑定撤销组合键，带shift
        tk.Frame(ctrlFrame, w=10).pack(side='left')
        tk.Button(ctrlFrame, text='完成', width=8, bg='white',
                  command=lambda: self.onClose(False)).pack(side="left", fill="y")
        tipsFrame = tk.Frame(self.win)
        tipsFrame.pack()
        tk.Label(tipsFrame, text="↓ ↓ ↓ 将任意图片拖入下方预览。然后点击按钮切换画笔，在图片上按住左键框选出想要的区域。",
                 fg='gray').pack(side='left')
        tk.Label(tipsFrame, text="同一种区域可绘制多个方框。", fg='blue').pack(side='left')
        tk.Label(tipsFrame, text="↓ ↓ ↓", fg='gray').pack(side='left')
        # initPanel()

        # def initCanvas():  # 初始化绘图板
        self.canvas = tk.Canvas(self.win, width=self.cW, height=self.cH,
                                bg="gray", cursor="plus", borderwidth=0)
        self.canvas.bind("<Button-1>", self.mouseDown)  # 鼠标点击
        self.canvas.bind("<B1-Motion>", self.mouseMove)  # 鼠标移动
        self.canvas.pack()
        hook_dropfiles(self.win, func=self.draggedFiles)  # 注册文件拖入
        self.canvasImg = None  # 当前在显示的图片
        # initCanvas()

        def initOCR():  # 初始化识别器
            canvasText = self.canvas.create_text(self.cW/2, self.cH/2, font=('', 15, 'bold'), fill='white', anchor="c",
                                                 text=f'引擎启动中，请稍候……')
            try:
                OCRe.start()  # 启动或刷新引擎
            except Exception as e:
                tk.messagebox.showerror(
                    '遇到了亿点小问题',
                    f'识别器初始化失败：{e}\n\n请检查配置有无问题！')
                self.win.attributes('-topmost', 1)  # 设置层级最前
                self.win.attributes('-topmost', 0)  # 然后立刻解除
                self.isAutoOCR.set(False)  # 关闭自动分析
                return
            finally:
                try:
                    self.canvas.delete(canvasText)  # 删除提示文字
                except:
                    pass
        initOCR()

        if defaultPath:  # 打开默认图片
            self.loadImage(defaultPath)

    def onClose(self, isAsk=True):  # 点击关闭。isAsk为T时询问。

        def getData():  # 将数据传给接口，然后关闭窗口
            area = [[], [], []]
            for i in range(3):
                for a in self.area[i]:
                    a00, a01, a10, a11 = round(
                        a[0][0]/self.imgScale), round(a[0][1]/self.imgScale), round(a[1][0]/self.imgScale), round(a[1][1]/self.imgScale)
                    if a00 > a10:  # x对调
                        a00, a10 = a10, a00
                    if a01 > a11:  # y对调
                        a01, a11 = a11, a01
                    area[i].append([(a00, a01), (a10, a11)])
            return {"size": self.imgSize, "area": area}

        if self.area[0] or self.area[1] or self.area[2]:  # 数据存在
            if isAsk:  # 需要问
                if tk.messagebox.askokcancel('关闭窗口', '要应用选区吗？'):  # 需要应用
                    Config.set("ignoreArea", getData())
            else:  # 不需要问
                Config.set("ignoreArea", getData())
        if self.closeSendData:  # 通信接口存在，则回传数据
            self.closeSendData()
        OCRe.stopByMode()  # 关闭OCR进程
        self.win.destroy()  # 销毁窗口

    def draggedFiles(self, paths):  # 拖入文件
        self.loadImage(paths[0].decode(  # 根据系统编码来解码
            Config.sysEncoding, errors='ignore'))

    def reLoadImage(self):  # 载入旧图片
        if self.lastPath:
            self.loadImage(self.lastPath)

    def loadImage(self, path):  # 载入新图片
        """载入图片"""
        try:
            img = Image.open(path)
        except Exception as e:
            tk.messagebox.showwarning(
                "遇到了一点小问题", f"图片载入失败。图片地址：\n{path}\n\n错误信息：\n{e}")
            self.win.attributes('-topmost', 1)  # 设置层级最前
            self.win.attributes('-topmost', 0)  # 然后立刻解除
            return
        # 检测图片大小
        if self.imgSize == (-1, -1):  # 初次设定
            self.imgSize = img.size
            # 计算 按宽和高 分别缩放的比例
            sw, sh = self.cW/img.size[0], self.cH/img.size[1]
            # 测试，按宽、还是高缩放，刚好填满画布
            if sw > sh:  # 按高
                self.imgReSize = (round(img.size[0]*sh), self.cH)
                self.imgScale = sh
            else:  # 按宽
                self.imgReSize = (self.cW, round(img.size[1]*sw))
                self.imgScale = sw
            self.imgSizeText.set(f'{self.imgSize[0]}x{self.imgSize[1]}')
        elif not self.imgSize == img.size:  # 尺寸不符合
            tk.messagebox.showwarning("图片尺寸错误！",
                                      f"当前图像尺寸限制为{self.imgSize[0]}x{self.imgSize[1]}，不允许加载{img.size[0]}x{img.size[1]}的图片。\n若要解除限制、更改为其他分辨率，请点击“清空”后重新拖入图片。")
            self.win.attributes('-topmost', 1)  # 设置层级最前
            self.win.attributes('-topmost', 0)  # 然后立刻解除
            return
        self.clearCanvasImage()  # 清理上次绘制的图像

        # OCR识别
        def runOCR():
            # 任务前：显示提示信息
            self.win.title(f"分析中…………")  # 改变标题
            pathStr = path if len(
                path) <= 50 else path[:50]+"……"  # 路径太长显示不全，截取
            canvasText = self.canvas.create_text(self.cW/2, self.cH/2, font=('', 15, 'bold'), fill='white', anchor="c",
                                                 text=f'图片分析中，请稍候……\n\n\n\n{pathStr}')
            self.win.update()  # 刷新窗口
            # 开始识别，耗时长
            data = OCRe.run(path)
            # 任务后：刷新提示信息
            self.canvas.delete(canvasText)  # 删除提示文字
            if data['code'] == 100:  # 存在内容
                if Config.get('isAreaWinAutoTbpu'):  # 需要后处理
                    tbpuClass = Config.get('tbpu').get(
                        Config.get('tbpuName'), None)
                    if tbpuClass:
                        name = os.path.basename(path)  # 带后缀的文件名
                        imgInfo = {'name': name,
                                   'path': path, 'size': img.size}
                        tbpu = tbpuClass()
                        data['data'], s = tbpu.run(data['data'], imgInfo)
                for o in data["data"]:  # 绘制矩形框
                    # 提取左上角、右下角的坐标
                    p1x = round(o['box'][0][0]*self.imgScale)+self.tran
                    p1y = round(o['box'][0][1]*self.imgScale)+self.tran
                    p2x = round(o['box'][2][0]*self.imgScale)+self.tran
                    p2y = round(o['box'][2][1]*self.imgScale)+self.tran
                    r1 = self.canvas.create_rectangle(
                        p1x, p1y, p2x, p2y, outline='white', width=2)  # 绘制白实线基底
                    r2 = self.canvas.create_rectangle(
                        p1x, p1y, p2x, p2y, outline='black', width=2, dash=4)  # 绘制黑虚线表层
                    self.canvas.tag_lower(r2)  # 移动到最下方
                    self.canvas.tag_lower(r1)
                    self.areaTextRec.append(r1)
                    self.areaTextRec.append(r2)
            elif not data["code"] == 101:  # 发生异常
                self.isAutoOCR.set(False)  # 关闭自动分析
                tk.messagebox.showwarning(
                    "遇到了一点小问题", f"图片分析失败。图片地址：\n{path}\n\n错误码：{str(data['code'])}\n\n错误信息：\n{str(data['data'])}")
                self.win.attributes('-topmost', 1)  # 设置层级最前
                self.win.attributes('-topmost', 0)  # 然后立刻解除
        if self.isAutoOCR.get():
            try:
                runOCR()
            except Exception as e:
                tk.messagebox.showerror('遇到了一点小问题', f'预览OCR失败：\n{e}')
                return
        self.win.title(f"选择区域 {path}")  # 改变标题
        # 缓存图片并显示
        img = img.resize(self.imgReSize, Image.ANTIALIAS)  # 改变图片大小
        self.imgFile = ImageTk.PhotoImage(img)  # 缓存图片
        self.canvasImg = self.canvas.create_image(
            0, 0, anchor='nw', image=self.imgFile)  # 绘制图片
        self.canvas.tag_lower(self.canvasImg)  # 该元素移动到最下方，防止挡住矩形们
        self.lastPath = path

    def changeMode(self, type_):  # 切换绘图模式
        if self.imgSize == (-1, -1):
            return
        self.areaType = type_
        for b in self.buttons:
            b["state"] = tk.NORMAL  # 启用所有按钮
            b["bg"] = self.areaColor[3]
        self.buttons[type_]["state"] = tk.DISABLED  # 禁用刚按下的按钮
        self.buttons[type_]["bg"] = self.areaColor[type_]  # 切换背景颜色

    def clearCanvasImage(self):  # 清除画布上的图片其文字框，不清理忽略框
        self.lastPath = ''
        if self.canvasImg:  # 删除图片
            self.canvas.delete(self.canvasImg)
        for t in self.areaTextRec:  # 删除文字框
            self.canvas.delete(t)
        self.areaTextRec = []

    def clearCanvas(self):  # 清除画布
        self.lastPath = ''
        self.win.title(f"选择区域")  # 改变标题
        self.area = [[], [], []]
        self.areaHistory = []
        self.areaTextRec = []
        self.areaType = -1
        self.areaTypeIndex = [-1, -1, -1]
        self.imgSize = (-1, -1)
        self.imgSizeText.set("未设定")
        self.canvas.delete(tk.ALL)
        for b in self.buttons:
            b["state"] = tk.NORMAL  # 启用所有按钮
            b["bg"] = self.areaColor[3]

    def revokeCanvas(self, e=None):  # 撤销一步
        if len(self.areaHistory) == 0:
            return
        self.canvas.delete(self.areaHistory[-1]["id"])  # 删除历史记录中最后绘制的矩形
        self.area[self.areaHistory[-1]["type"]].pop()  # 删除对应类型的最后一个矩形数据
        self.areaHistory.pop()  # 删除历史记录

    def mouseDown(self, event):  # 鼠标按下，生成新矩形
        if self.areaType == -1:
            return
        x, y = event.x, event.y
        if x > self.imgReSize[0]:  # 防止越界
            x = self.imgReSize[0]
        elif x < 0:
            x = 0
        if y > self.imgReSize[1]:
            y = self.imgReSize[1]
        elif y < 0:
            y = 0
        c = self.areaColor[self.areaType]
        id = self.canvas.create_rectangle(  # 绘制新图
            x+self.tran, y+self.tran, x+self.tran, y+self.tran,  width=2, activefill=c, outline=c)
        self.area[self.areaType].append([(x, y), (x, y)])  # 向对应列表中增加1个矩形
        self.areaHistory.append({"id": id, "type": self.areaType})  # 载入历史记录

    def mouseMove(self, event):  # 鼠标拖动，刷新最后的矩形
        if self.areaType == -1:
            return
        x, y = event.x, event.y
        if x > self.imgReSize[0]:  # 防止越界
            x = self.imgReSize[0]
        elif x < 0:
            x = 0
        if y > self.imgReSize[1]:
            y = self.imgReSize[1]
        elif y < 0:
            y = 0
        x0, y0 = self.area[self.areaType][-1][0][0], self.area[self.areaType][-1][0][1]
        # 刷新历史记录中最后的图形的坐标
        self.canvas.coords(
            self.areaHistory[-1]["id"], x0+self.tran, y0+self.tran, x+self.tran, y+self.tran)
        self.area[self.areaType][-1][1] = (x, y)  # 刷新右下角点
