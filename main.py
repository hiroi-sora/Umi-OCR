from distutils.command.config import config
from selectAreaWin import SelectAreaWin  # 子窗口
from asset import IconPngBase64, GetHelpText  # 资源
from callingOCR import CallingOCR  # OCR调用接口
from config import Config

import os
import time
import asyncio  # 异步
import threading  # 线程
import keyboard  # 绑定快捷键
from PIL import Image, ImageGrab  # 图像，剪贴板
import tkinter as tk
import tkinter.filedialog
from tkinter import Variable, ttk
from windnd import hook_dropfiles  # 文件拖拽
from pyperclip import copy as pyperclipCopy  # 剪贴板
from webbrowser import open as webOpen  # “关于”面板打开项目网址

ProjectVer = "1.2.4"  # 版本号
ProjectName = f"Umi-OCR 批量图片转文字 v{ProjectVer}"  # 名称
ProjectWeb = "https://github.com/hiroi-sora/Umi-OCR"
TempFilePath = "Umi-OCR_temp"


class Win:
    def __init__(self):
        self.imgDict = {}  # 当前载入的图片信息字典，key为表格组件id。必须为有序字典，python3.6以上默认是。
        self.isRunning = 0  # 0未在运行，1正在运行，2正在停止
        self.lockWidget = []  # 需要运行时锁定的组件

        # 1.初始化主窗口
        def initWin():
            self.win = tk.Tk()
            self.win.title(ProjectName)
            # 窗口大小与位置
            w, h = 360, 500  # 窗口初始大小与最小大小
            ws, hs = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            x, y = round(ws/2 - w/2), round(hs/2 - h/2)  # 初始位置，屏幕正中
            self.win.minsize(w, h)  # 最小大小
            self.win.geometry(f"{w}x{h}+{x}+{y}")  # 初始大小与位置
            self.win.protocol("WM_DELETE_WINDOW", self.onClose)  # 窗口关闭
            # 图标
            self.iconImg = tkinter.PhotoImage(
                data=IconPngBase64)  # 载入图标，base64转
            self.win.iconphoto(False, self.iconImg)  # 设置窗口图标
        initWin()

        # 2.初始化变量、配置项
        def initVar():
            self.cfgVar = {  # 设置项tk变量
                # 读取剪贴板设置
                "isGlobalHotkey": tk.BooleanVar(),  # T时绑定全局快捷键
                "isNeedCopy": tk.BooleanVar(),  # T时识别完成后自动复制文字
                "globalHotkey": tk.StringVar(),  # 全局快捷键
                # 输出文件设置
                "isOutputFile": tk.BooleanVar(),  # T时输出内容写入本地文件
                "isOpenExplorer": tk.BooleanVar(),  # T时任务完成后打开资源管理器到输出目录。isOutputFile为T时才管用
                "isOpenOutputFile": tk.BooleanVar(),  # T时任务完成后打开输出文件。isOutputFile为T时才管用
                "outputFilePath": tk.StringVar(),  # 输出文件目录
                "outputFileName": tk.StringVar(),  # 输出文件名称
                # 输出格式设置
                "isOutputDebug": tk.BooleanVar(),  # T时输出调试信息
                "isIgnoreNoText": tk.BooleanVar(),  # T时忽略(不输出)没有文字的图片信息
                "outputStyle": tk.IntVar(),  # 1：纯文本，2：Markdown
                # 识别器设置
                "ocrToolPath": tk.StringVar(),  # 识别器路径
                "imageSuffix": tk.StringVar(),  # 图片后缀
            }
            Config.initValue(self.cfgVar)  # 初始化设置项

            # 面板值改变时，更新到配置值，并写入本地
            self.saveTimer = None  # 计时器，改变面板值一段时间后写入本地

            def configSave():  # 保存值的事件
                Config.save()
                self.saveTimer = None

            def valueChange(key):  # 值改变的事件
                Config.update(key)  # 更新配置项
                if Config.isSaveItem(key):
                    if self.saveTimer:  # 计时器已存在，则停止已存在的
                        self.win.after_cancel(self.saveTimer)
                        self.saveTimer = None
                    self.saveTimer = self.win.after(200, configSave)
            for key in self.cfgVar:
                self.cfgVar[key].trace(  # 跟踪值改变事件
                    "w", lambda *e, key=key: valueChange(key))
            self.isNeedCopy = False  # 标志值，T时识图后复制文字
        initVar()

        # 3.初始化组件
        def initTop():  # 顶部按钮
            tk.Frame(self.win, height=5).pack(side='top')
            fr = tk.Frame(self.win)
            fr.pack(side='top', fill="x", padx=5)
            # 右侧按钮
            self.btnRun = tk.Button(
                fr, text='开始任务', width=12, height=2,  command=self.run)
            self.btnRun.pack(side='right', padx=5)
            # 左侧文本和进度条
            vFrame2 = tk.Frame(fr)
            vFrame2.pack(side='top', fill='x')
            labelUse = tk.Label(vFrame2, text="使用说明",
                                fg="gray", cursor="hand2")
            labelUse.pack(side='left', padx=5)
            labelUse.bind('<Button-1>', self.showInstructions)  # 绑定鼠标左键点击
            self.labelPercentage = tk.Label(vFrame2, text="0%")  # 进度百分比 99%
            self.labelPercentage.pack(side='right', padx=2)
            self.labelFractions = tk.Label(vFrame2, text="0/0")  # 进度分数 99/100
            self.labelFractions.pack(side='right')
            self.labelTime = tk.Label(vFrame2, text="0s")  # 已用时间 12.3s
            self.labelTime.pack(side='right', padx=5)
            self.progressbar = ttk.Progressbar(fr)
            self.progressbar.pack(side='top', padx=5, fill="x")
        initTop()

        self.notebook = ttk.Notebook(self.win)  # 初始化选项卡组件
        self.notebook.pack(expand=True, fill=tk.BOTH)  # 填满父组件

        def initTab1():  # 表格卡
            tabFrame = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebook.add(tabFrame, text=f'{"处理列表": ^10s}')
            # 顶栏
            fr1 = tk.Frame(tabFrame)
            fr1.pack(side='top', fill='x', pady=2)
            tk.Button(fr1, text=' 浏览 ',  command=self.openFileWin).pack(
                side='left', padx=5)
            tk.Label(fr1, text="或直接拖入").pack(side='left')
            tk.Button(fr1, text='清空表格', width=12, command=self.clearTable).pack(
                side='right')
            tk.Button(fr1, text='移除选中图片', width=12, command=self.delImgList).pack(
                side='right', padx=5)
            # 表格主体
            fr2 = tk.Frame(tabFrame)
            fr2.pack(side='top', fill='both')
            self.table = ttk.Treeview(
                master=fr2,  # 父容器
                height=50,  # 表格显示的行数,height行
                columns=['name', 'time', 'score'],  # 显示的列
                show='headings',  # 隐藏首列
            )
            hook_dropfiles(self.table, func=self.draggedImages)  # 注册文件拖入
            self.table.pack(expand=True, side="left", fill='both')
            self.table.heading('name', text='文件名称')
            self.table.heading('time', text='耗时')
            self.table.heading('score', text='置信度')
            self.table.column('name', minwidth=40)
            self.table.column('time', width=20, minwidth=20)
            self.table.column('score', width=30, minwidth=30)
            vbar = tk.Scrollbar(  # 绑定滚动条
                fr2, orient='vertical', command=self.table.yview)
            vbar.pack(side="left", fill='y')
            self.table["yscrollcommand"] = vbar.set
        initTab1()

        def initTab2():  # 输出卡
            self.tabFrameOutput = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebook.add(self.tabFrameOutput, text=f'{"识别内容": ^10s}')
            fr1 = tk.Frame(self.tabFrameOutput)
            fr1.pack(side='top', fill='x', pady=2)
            self.isAutoRoll = tk.IntVar()
            self.isAutoRoll.set(1)
            tk.Checkbutton(fr1, variable=self.isAutoRoll, text="自动滚动").pack(
                side='left')
            tk.Button(fr1, text='清空', width=6,
                      command=lambda: self.textOutput.delete('1.0', tk.END)).pack(side='right')
            tk.Button(fr1, text='复制文字', width=8,
                      command=lambda: pyperclipCopy(self.textOutput.get("1.0", tk.END))).pack(side='right', padx=5)
            tk.Button(fr1, text='剪贴板读取', width=10,
                      command=self.runClipboard).pack(side='right', padx=5)
            fr2 = tk.Frame(self.tabFrameOutput)
            fr2.pack(side='top', fill='both')
            vbar = tk.Scrollbar(fr2, orient='vertical')  # 滚动条
            vbar.pack(side="right", fill='y')
            self.textOutput = tk.Text(fr2, height=500, width=500)
            self.textOutput.pack(fill='both', side="left")
            vbar["command"] = self.textOutput.yview
            self.textOutput["yscrollcommand"] = vbar.set
        initTab2()

        def initTab3():  # 设置卡
            tabFrame = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebook.add(tabFrame, text=f'{"设置": ^10s}')

            def initOptFrame():  # 初始化可滚动画布 及 内嵌框架
                optVbar = tk.Scrollbar(
                    tabFrame, orient="vertical")  # 创建滚动条
                optVbar.pack(side="right", fill="y")
                self.optCanvas = tk.Canvas(
                    tabFrame, highlightthickness=0)  # 创建画布，用于承载框架。highlightthickness取消高亮边框
                self.optCanvas.pack(side="left", fill="both",
                                    expand="yes")  # 填满父窗口
                self.optCanvas["yscrollcommand"] = optVbar.set  # 绑定滚动条
                optVbar["command"] = self.optCanvas.yview
                self.optFrame = tk.Frame(self.optCanvas)  # 容纳设置项的框架
                self.optFrame.pack()
                self.optCanvas.create_window(  # 框架塞进画布
                    (0, 0), window=self.optFrame, anchor="nw")
            initOptFrame()

            LabelFramePadY = 3  # 每个区域上下间距

            def initArea():  # 忽略区域设置
                self.areaLabel = tk.LabelFrame(
                    self.optFrame, text="忽略图片中某些区域内的文字")
                self.areaLabel.pack(side='top', fill='x',
                                    ipady=2, pady=LabelFramePadY, padx=4)
                self.areaLabel.grid_columnconfigure(0, minsize=4)
                wid = tk.Button(self.areaLabel, text='添加区域',
                                command=self.openSelectArea)
                wid.grid(column=1, row=0, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Button(self.areaLabel, text='清空区域',
                                command=self.clearArea)
                wid.grid(column=1, row=1, sticky="w")
                self.lockWidget.append(wid)
                self.areaLabel.grid_rowconfigure(2, minsize=10)
                # tk.Button(self.areaLabel, text='读取预设',
                #           command=self.showTest).grid(column=1, row=3, sticky="w")
                # tk.Button(self.areaLabel, text='保存预设',
                #           command=self.showTest).grid(column=1, row=4, sticky="w")
                self.areaLabel.grid_columnconfigure(2, minsize=4)
                self.canvasHeight = 140  # 画板高度不变，宽度根据选区回传数据调整
                self.canvas = tk.Canvas(self.areaLabel, width=249, height=self.canvasHeight,
                                        bg="black")
                self.canvas.grid(column=3, row=0, rowspan=10)
            initArea()

            def initClipboard():  # 剪贴板设置
                def addHotkey(hotkey):  # 注册新快捷键
                    if hotkey == "":
                        Config.set("isGlobalHotkey", False)
                        tk.messagebox.showwarning("提示",
                                                  f"请先录制快捷键")
                        return
                    try:
                        keyboard.add_hotkey(
                            hotkey, self.runClipboard, suppress=False)  # 添加新的
                    except ValueError as err:
                        print(f"注册快捷键异常：{err}")
                        Config.set("isGlobalHotkey", False)
                        Config.set("globalHotkey", "")
                        tk.messagebox.showwarning("提示",
                                                  f"无法注册快捷键【{hotkey}】")

                def updateHotket():  # 刷新快捷键
                    try:
                        keyboard.unhook_all_hotkeys()  # 移除 所有旧快捷键
                    except Exception as err:  # 影响不大。未注册过就调用移除 会报这个异常
                        # print(f"移除快捷键异常：{err}")
                        pass
                    if Config.get("isGlobalHotkey"):  # 添加
                        addHotkey(Config.get("globalHotkey"))
                updateHotket()  # 初始化时执行一次

                def readHotkey():  # 录制快捷键
                    hotkey = keyboard.read_hotkey(suppress=False)
                    if hotkey == "esc":  # 不绑定ESC
                        return
                    Config.set("globalHotkey", hotkey)  # 写入设置
                    updateHotket()

                def delHotkey():  # 清除快捷键
                    Config.set("globalHotkey", "")
                    Config.set("isGlobalHotkey", False)
                    updateHotket()

                areaLabel = tk.LabelFrame(
                    self.optFrame, text="从剪贴板读取图片")
                areaLabel.pack(side='top', fill='x',
                                    ipady=2, pady=LabelFramePadY, padx=4)
                fr1 = tk.Frame(areaLabel)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                wid = tk.Checkbutton(fr1, variable=self.cfgVar["isGlobalHotkey"],
                                     text="启用全局快捷键（在其它窗口也可响应）", command=updateHotket)
                wid.grid(column=0, row=0, columnspan=9, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr1, variable=self.cfgVar["isNeedCopy"],
                                     text="自动复制识别文本")
                wid.grid(column=0, row=1, columnspan=9, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Button(fr1, text='录制按键',
                                command=readHotkey)
                wid.grid(column=0, row=2, sticky="w")
                self.lockWidget.append(wid)
                tk.Label(fr1, textvariable=self.cfgVar["globalHotkey"]).grid(
                    column=2, row=2,  sticky="nsew")
                wid = tk.Button(fr1, text='清除', width=8,
                                command=delHotkey)
                wid.grid(column=3, row=2, sticky="w")
                self.lockWidget.append(wid)
                fr1.grid_columnconfigure(2, weight=1)
                fr1.grid_columnconfigure(1, minsize=6)
            initClipboard()

            def initOutFile():  # 输出文件设置
                frameOutFile = tk.LabelFrame(self.optFrame, text="输出设置")
                frameOutFile.pack(side='top', fill='x',
                                  ipady=2, pady=LabelFramePadY, padx=4)

                fr1 = tk.Frame(frameOutFile)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                wid = tk.Checkbutton(
                    fr1, variable=self.cfgVar["isOutputFile"], text="将识别内容写入本地文件")
                wid.grid(column=0, row=0, columnspan=2, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr1, text="输出调试信息",
                                     variable=self.cfgVar["isOutputDebug"])
                wid.grid(column=0, row=1, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr1, text="忽略无文字的图片",
                                     variable=self.cfgVar["isIgnoreNoText"],)
                wid.grid(column=1, row=1, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr1, text="完成后打开文件",
                                     variable=self.cfgVar["isOpenOutputFile"])
                wid.grid(column=0, row=2, sticky="w")
                wid = tk.Checkbutton(fr1, text="完成后打开目录",
                                     variable=self.cfgVar["isOpenExplorer"],)
                wid.grid(column=1, row=2, sticky="w")
                wid = tk.Radiobutton(
                    fr1, text='纯文本.txt文件', value=1, variable=self.cfgVar["outputStyle"],)
                wid.grid(column=0, row=3, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Radiobutton(
                    fr1, text='Markdown风格.md文件', value=2, variable=self.cfgVar["outputStyle"],)
                wid.grid(column=1, row=3, sticky="w")
                self.lockWidget.append(wid)
                tk.Label(fr1, fg="gray",
                         text="下面两项为空时，默认输出到第一张图片所在的文件夹"
                         ).grid(column=0, row=4, columnspan=2, sticky="nsew")

                fr2 = tk.Frame(frameOutFile)
                fr2.pack(side='top', fill='x', pady=2, padx=5)
                tk.Label(fr2, text="输出目录：").grid(column=0, row=3, sticky="w")
                enOutPath = tk.Entry(
                    fr2, textvariable=self.cfgVar["outputFilePath"])
                enOutPath.grid(column=1, row=3,  sticky="nsew")
                self.lockWidget.append(enOutPath)
                fr2.grid_rowconfigure(4, minsize=2)  # 第二行拉开间距
                tk.Label(fr2, text="输出文件名：").grid(column=0, row=5, sticky="w")
                enOutName = tk.Entry(
                    fr2, textvariable=self.cfgVar["outputFileName"])
                enOutName.grid(column=1, row=5, sticky="nsew")
                self.lockWidget.append(enOutName)
                fr2.grid_columnconfigure(1, weight=1)  # 第二列自动扩充
            initOutFile()

            def initOcrUI():  # 识别器exe与图片后缀设置
                frameOCR = tk.LabelFrame(
                    self.optFrame, text="识别器设置  [切换多国语言和不同格式图片]")
                frameOCR.pack(side='top', fill='x', ipady=2,
                              pady=LabelFramePadY, padx=4)

                fr1 = tk.Frame(frameOCR)
                fr1.pack(side='top', fill='x', pady=2, padx=5)

                tk.Label(fr1, text="识别器路径：").grid(column=0, row=0, sticky="w")
                enEXE = tk.Entry(fr1, textvariable=self.cfgVar["ocrToolPath"])
                enEXE.grid(column=1, row=0,  sticky="nsew")
                self.lockWidget.append(enEXE)

                tk.Label(fr1, text="图片后缀：").grid(column=0, row=2, sticky="w")
                enInSuffix = tk.Entry(
                    fr1, textvariable=self.cfgVar["imageSuffix"])
                enInSuffix.grid(column=1, row=2, sticky="nsew")
                self.lockWidget.append(enInSuffix)
                fr1.grid_columnconfigure(1, weight=1)
                fr1.grid_rowconfigure(1, minsize=2)
            initOcrUI()

            def initAbout():  # 关于面板
                frameAbout = tk.LabelFrame(
                    self.optFrame, text="关于")
                frameAbout.pack(side='top', fill='x', ipady=2,
                                pady=LabelFramePadY, padx=4)
                tk.Label(frameAbout, image=self.iconImg).pack()  # 图标
                tk.Label(frameAbout, text=ProjectName, fg="gray").pack()
                labelWeb = tk.Label(frameAbout, text=ProjectWeb, cursor="hand2",
                                    fg="deeppink")
                labelWeb.pack()  # 文字
                labelWeb.bind(  # 绑定鼠标左键点击，打开网页
                    '<Button-1>', self.openProjectWeb)
            initAbout()

            def initOptFrameWH():  # 初始化框架的宽高
                self.optFrame.update()  # 强制刷新
                rH = self.optFrame.winfo_height()  # 由组件撑起的 框架高度
                self.optCanvas.config(scrollregion=(0, 0, 0, rH))  # 画布内高度为框架高度
                self.optFrame.pack_propagate(False)  # 禁用框架自动宽高调整
                self.optFrame["height"] = rH  # 手动还原高度。一次性设置，之后无需再管。
                self.optCanvasWidth = 1  # 宽度则是随窗口大小而改变。

                def onCanvasResize(event):  # 绑定画布大小改变事件
                    cW = event.width-3  # 当前 画布宽度
                    if not cW == self.optCanvasWidth:  # 若与上次不同：
                        self.optFrame["width"] = cW  # 修改设置页 框架宽度
                        self.optCanvasWidth = cW
                self.optCanvas.bind(  # 绑定画布大小改变事件。只有画布组件前台显示时才会触发，减少性能占用
                    '<Configure>', onCanvasResize)

                def onCanvasMouseWheel(event):  # 绑定画布中滚轮滚动事件
                    self.optCanvas.yview_scroll(
                        1 if event.delta < 0 else -1, "units")
                self.optCanvas.bind_all("<MouseWheel>", onCanvasMouseWheel)
            initOptFrameWH()
        initTab3()

        # 4.绑定快捷键
        def bindKey():
            self.win.bind("<Control-V>", self.runClipboard)
        bindKey()

        self.win.mainloop()

    # 加载图片 ===============================================

    def draggedImages(self, paths):  # 拖入图片
        if not self.isRunning == 0:
            return
        pathList = []
        for p in paths:  # byte转字符串
            pathList.append(p.decode("gbk"))
        self.addImagesList(pathList)

    def openFileWin(self):  # 打开选择文件窗
        if not self.isRunning == 0:
            return
        suf = Config.get("imageSuffix")  # 许可后缀
        paths = tk.filedialog.askopenfilenames(
            title='选择图片', filetypes=[('图片', suf)])
        self.addImagesList(paths)

    def addImagesList(self, paths):  # 添加一批图片列表
        suf = Config.get("imageSuffix").split()  # 许可后缀列表

        def addImage(path):  # 添加一张图片。传入路径，许可后缀。
            path = path.replace("/", "\\")  # 浏览是左斜杠，拖入是右斜杠；需要统一
            if suf and os.path.splitext(path)[1].lower() not in suf:
                return  # 需要判别许可后缀 且 文件后缀不在许可内，不添加。
            # 检测是否重复
            for key, value in self.imgDict.items():
                if value["path"] == path:
                    return
            # 检测是否可用
            try:
                s = Image.open(path).size
            except Exception as e:
                tk.messagebox.showwarning(
                    "遇到了一点小问题", f"图片载入失败。图片地址：\n{path}\n\n错误信息：\n{e}")
                return
            # 计算路径
            p = os.path.abspath(os.path.join(path, os.pardir))  # 父文件夹
            if not Config.get("outputFilePath"):  # 初始化输出路径
                Config.set("outputFilePath", p)
            if not Config.get("outputFileName"):  # 初始化输出文件名
                n = f"[转文字]_{os.path.basename(p)}"
                Config.set("outputFileName", n)
            # 加入待处理列表
            name = os.path.basename(path)  # 带后缀的文件名
            tableInfo = (name, "", "")
            id = self.table.insert('', 'end', values=tableInfo)  # 添加到表格组件中
            dictInfo = {"name": name, "path": path, "size": s}
            self.imgDict[id] = (dictInfo)  # 添加到字典中

        for path in paths:  # 遍历拖入的所有路径
            if os.path.isdir(path):  # 若是目录
                subFiles = os.listdir(path)  # 遍历子文件
                for s in subFiles:
                    addImage(path+"\\"+s)  # 添加
            elif os.path.isfile(path):  # 若是文件：
                addImage(path)  # 直接添加

    def runClipboard(self, e=None):  # 识别剪贴板
        if not self.isRunning == 0:  # 正在运行，不执行
            return
        img = ImageGrab.grabclipboard()  # 读取
        if not isinstance(img, Image.Image):
            return  # 未读到图像
        # 窗口恢复前台，并临时置顶
        if self.win.state() == "iconic":  # 窗口最小化状态下
            self.win.state("normal")  # 恢复前台状态
        self.win.attributes('-topmost', 1)  # 设置层级最前
        self.win.attributes('-topmost', 0)  # 然后立刻解除
        # 保存临时文件
        if not os.path.exists(TempFilePath):  # 创建临时文件夹
            os.makedirs(TempFilePath)
        else:  # 清空临时文件夹
            delList = os.listdir(TempFilePath)
            for f in delList:
                p = f"{TempFilePath}\\{f}"
                if os.path.isfile(p):
                    os.remove(p)
        imgPath = f"{TempFilePath}\\temp_{int(time.time()*1000)}.png"
        img.save(imgPath)
        # 刷新自动复制
        if Config.get("isNeedCopy"):
            self.isNeedCopy = True
        # 载入队列
        imgPath = os.path.abspath(imgPath)  # 转绝对路径
        self.clearTable()  # 清空表格
        self.addImagesList([imgPath])  # 加入表格
        self.run()  # 开始执行
        self.notebook.select(self.tabFrameOutput)  # 转到输出卡

    # 忽略区域 ===============================================

    def openSelectArea(self):  # 打开选择区域
        if not self.isRunning == 0:
            return
        defaultPath = ""
        if self.imgDict:
            defaultPath = next(iter(self.imgDict.values()))["path"]
        self.win.attributes("-disabled", 1)  # 禁用父窗口
        SelectAreaWin(self.closeSelectArea, defaultPath)

    def closeSelectArea(self):  # 关闭选择区域，获取选择区域数据
        self.win.attributes("-disabled", 0)  # 启用父窗口
        area = Config.get("ignoreArea")
        if not area:
            return
        self.areaLabel["text"] = f"忽略区域 生效分辨率：{area['size'][0]}x{area['size'][1]}"
        self.canvas.delete(tk.ALL)  # 清除画布
        scale = self.canvasHeight / area['size'][1]  # 显示缩放比例
        width = int(self.canvasHeight * (area['size'][0] / area['size'][1]))
        self.canvas["width"] = width
        areaColor = ["red", "green", "gold1"]
        for i in range(3):
            for a in area['area'][i]:
                x0, y0 = a[0][0]*scale, a[0][1]*scale,
                x1, y1 = a[1][0]*scale, a[1][1]*scale,
                self.canvas.create_rectangle(
                    x0, y0, x1, y1,  fill=areaColor[i])  # 绘制新图

    def clearArea(self):  # 清空忽略区域
        Config.set("ignoreArea", None)
        self.areaLabel["text"] = "忽略图片中某些区域内的文字"
        self.canvas.delete(tk.ALL)  # 清除画布
        self.canvas["width"] = int(self.canvasHeight * (16/9))

    # 表格操作 ===============================================

    def clearTable(self):  # 清空表格
        if not self.isRunning == 0:
            return
        self.progressbar["value"] = 0
        self.labelPercentage["text"] = "0%"
        self.labelFractions["text"] = "0/0"
        self.labelTime["text"] = "0s"
        Config.set("outputFilePath", "")
        Config.set("outputFileName", "")
        self.imgDict = {}
        chi = self.table.get_children()
        for i in chi:
            self.table.delete(i)  # 表格组件移除

    def delImgList(self):  # 图片列表中删除选中
        if not self.isRunning == 0:
            return
        chi = self.table.selection()
        for i in chi:
            self.table.delete(i)
            del self.imgDict[i]  # 字典删除

    def setRunning(self, r):  # 设置运行状态。0停止，1运行中，2停止中
        self.isRunning = r
        state = ""  # 组件状态
        if r == 0:
            self.btnRun["text"] = "开始任务"
            self.btnRun['state'] = "normal"
            state = "normal"
        elif r == 1:
            self.btnRun["text"] = "停止任务"
            self.btnRun['state'] = "normal"
            state = "disable"
        elif r == 2:
            self.btnRun["text"] = "正在停止"
            self.btnRun['state'] = "disable"
            state = "normal"
        for w in self.lockWidget:  # 改变组件状态（禁用，启用）

            w['state'] = state

    def run(self):  # 开始任务，创建新线程和事件循环
        if self.isRunning == 0:  # 未在运行，开始运行
            if not self.imgDict:
                return
            # 检测识别器存在
            ocrToolPath = Config.get("ocrToolPath")
            if not os.path.exists(ocrToolPath):
                tk.messagebox.showerror(
                    '遇到了一点小问题', f'未在以下地址找到识别器！\n{ocrToolPath}')
                return
            # 创建输出文件
            if Config.get("isOutputFile"):
                suffix = ".txt" if Config.get("outputStyle") == 1 else ".md"
                outPath = Config.get("outputFilePath") + \
                    "\\" + Config.get("outputFileName")+suffix
                try:
                    if os.path.exists(outPath):  # 文件存在
                        os.remove(outPath)  # 删除文件
                    open(outPath, 'w').close()  # 创建文件
                except FileNotFoundError:
                    tk.messagebox.showerror(
                        '遇到了亿点小问题', f'创建输出文件失败。请检查以下地址是否正确。\n{outPath}')
                    return
                except Exception as e:
                    tk.messagebox.showerror(
                        '遇到了亿点小问题', f'创建输出文件失败。文件地址：\n{outPath}\n\n错误信息：\n{e}')
                    return
            self.setRunning(1)
            # 在当前线程下创建事件循环，在start_loop里面启动它
            newLoop = asyncio.new_event_loop()
            # 通过当前线程开启新的线程去启动事件循环
            threading.Thread(target=self.getLoop, args=(newLoop,)).start()
            # 在新线程中事件循环不断“游走”执行
            asyncio.run_coroutine_threadsafe(self.run_(), newLoop)
        elif self.isRunning == 1:  # 正在运行，停止运行
            self.setRunning(2)

    def getLoop(self, loop):  # 获取事件循环
        self.loop = loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def run_(self):  # 异步，执行任务
        # 这个函数非常，非常之丑
        # 有生之年一定，一定重构
        self.labelPercentage["text"] = "初始化"
        isOutputFile = Config.get("isOutputFile")  # 是否输出文件
        isOutputDebug = Config.get("isOutputDebug")  # 是否输出调试
        isIgnoreNoText = Config.get("isIgnoreNoText")  # 是否忽略无字图片
        outputStyle = Config.get("outputStyle")  # 输出风格
        areaInfo = Config.get("ignoreArea")
        if isOutputFile:
            outputPath = Config.get("outputFilePath")  # 输出路径（文件夹）
            suffix = ".txt" if outputStyle == 1 else ".md"
            outputFile = outputPath+"\\" + \
                Config.get("outputFileName")+suffix  # 输出文件

        def output(outStr, type_):  # 输出字符串
            """
            debug ：调试信息
            text ：正文
            name ：文件名
            none ：不做修改
            """
            # 写入输出面板，无需格式
            self.textOutput.insert(tk.END, f"\n{outStr}\n")
            if self.isAutoRoll.get():  # 需要自动滚动
                self.textOutput.see(tk.END)

            # 写入本地文件，按照格式
            if isOutputFile:
                if outputStyle == 1:  # 纯文本风格
                    if type_ == "debug":
                        outStr = f"```\n{outStr}```\n"
                    elif type_ == "name":
                        outStr = f"\n\n≦ {outStr} ≧\n"
                elif outputStyle == 2:  # markdown风格
                    if type_ == "debug":
                        outStr = f"```\n{outStr}```\n"
                    elif type_ == "text":
                        outList = outStr.split("\n")
                        outStr = ""
                        for i in outList:
                            outStr += f"> {i}  \n"
                    elif type_ == "name":
                        path = outStr.replace(" ", "%20")
                        outStr = f"---\n![{outStr}]({path})\n[{outStr}]({path})\n"
                with open(outputFile, "a", encoding='utf-8') as f:  # 追加写入本地文件
                    f.write(outStr)

        def close():  # 关闭所有异步相关的东西
            del self.ocr  # 关闭OCR进程
            self.loop.stop()  # 关闭异步事件循环
            self.setRunning(0)
            self.labelPercentage["text"] = "已终止"

        def analyzeText(oget, img):  # 分析一张图转出的文字
            def isInBox(aPos0, aPos1, bPos0, bPos1):  # 检测框左上、右下角，待测者左上、右下角
                return bPos0[0] >= aPos0[0] and bPos0[1] >= aPos0[1] and bPos1[0] <= aPos1[0] and bPos1[1] <= aPos1[1]

            def isIden():  # 是否识别区域模式
                if areaInfo["area"][1]:  # 需要检测
                    for o in oget:  # 遍历每一个文字块
                        for a in areaInfo["area"][1]:  # 遍历每一个检测块
                            if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                                return True
            text = ""
            textDebug = ""  # 调试信息
            score = 0  # 平均置信度
            scoreNum = 0

            # 无需忽略区域
            if not areaInfo or not areaInfo["size"][0] == img["size"][0] or not areaInfo["size"][1] == img["size"][1]:

                for i in oget:
                    text += i["text"]+"\n"
                    score += i["score"]
                    scoreNum += 1

            # 忽略模式2
            elif isIden():
                fn = 0  # 记录忽略的数量
                for o in oget:
                    flag = True
                    for a in areaInfo["area"][2]:  # 遍历每一个检测块
                        if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                            flag = False  # 踩到任何一个块，GG
                            break
                    if flag:
                        text += o["text"]+"\n"
                        score += o["score"]
                        scoreNum += 1
                    else:
                        fn += 1
                if isOutputDebug:
                    textDebug = f"忽略模式2：忽略{fn}条\n"

            # 忽略模式1
            else:
                fn = 0  # 记录忽略的数量
                for o in oget:
                    flag = True
                    for a in areaInfo["area"][0]:  # 遍历每一个检测块
                        if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                            flag = False  # 踩到任何一个块，GG
                            break
                    if flag:
                        text += o["text"]+"\n"
                        score += o["score"]
                        scoreNum += 1
                    else:
                        fn += 1
                if isOutputDebug:
                    textDebug = f"忽略模式1：忽略{fn}条\n"

            if text and not scoreNum == 0:  # 区域内有文本，计算置信度
                score /= scoreNum
                score = str(score)  # 转文本
            else:
                score = "1"  # 区域内没有文本，置信度为1
            return text, textDebug, score

        # 开始
        startStr = f"任务开始时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
        output(startStr, "text")
        if isOutputDebug:
            if areaInfo:
                startStr = f'忽略区域：开启\n适用分辨率：{areaInfo["size"]}\n'
                startStr += f'忽略区域1：{areaInfo["area"][0]}\n'
                startStr += f'识别区域：{areaInfo["area"][1]}\n'
                startStr += f'忽略区域2：{areaInfo["area"][2]}\n'
            else:
                startStr = f"忽略区域：关闭\n"
            output(startStr, "debug")
        # 创建OCR进程
        self.ocr = CallingOCR(Config.get("ocrToolPath"))
        # 初始化UI
        for key in self.imgDict.keys():  # 清空表格参数
            self.table.set(key, column='time', value="")
            self.table.set(key, column='score', value="")
        allNum, nowNum = len(self.imgDict), 0
        startTime = time.time()  # 开始时间
        costTime = 0
        self.progressbar["maximum"] = allNum
        self.progressbar["value"] = 0
        self.labelPercentage["text"] = "0%"
        self.labelFractions["text"] = f"0/{allNum}"
        self.labelTime["text"] = "0s"
        numOK = 0  # 成功数量
        numNON = 0  # 不存在数量
        numERR = 0  # 出错数量

        # 主任务循环
        for key, value in self.imgDict.items():
            try:
                if not self.isRunning == 1:  # 需要停止
                    close()
                    return
                oget = self.ocr.run(value["path"])  # 调用图片识别
                # 计数
                nowNum += 1  # 当前完成个数
                costTimeNow = time.time() - startTime  # 当前总花费时间
                needTimeStr = str(costTimeNow-costTime)  # 单个花费时间
                costTime = round(costTimeNow, 2)  # 刷新花费时间
                self.progressbar["value"] = nowNum
                self.labelPercentage["text"] = f"{round((nowNum/allNum)*100)}%"
                self.labelFractions["text"] = f"{nowNum}/{allNum}"
                self.labelTime["text"] = f"{costTime}s"
                self.table.set(key, column='time',
                               value=needTimeStr[:4])  # 时间写入表格
                # 分析数据
                dataStr = ""
                textDebug = ""
                if oget['code'] == 100:  # 成功
                    numOK += 1
                    dataStr, textDebug, score = analyzeText(
                        oget['data'], value)  # 获取文字
                    if self.isNeedCopy:  # 识图后复制到剪贴板
                        pyperclipCopy(dataStr)
                elif oget['code'] == 101:  # 无文字
                    numNON += 1
                    score = "无文字"
                else:  # 识别失败
                    numERR += 1
                    dataStr = "识别失败"  # 不管开不开输出调试，都要输出报错
                    dataStr += f"，错误码：{oget['code']}\n错误信息：{str(oget['data'])}\n"
                    score = "失败"
                self.isNeedCopy = False  # 成功与否都将复制标志置F

                # 写入表格
                self.table.set(key, column='score', value=score[:4])
                # 格式化输出
                if isIgnoreNoText and not dataStr:
                    continue  # 忽略无字图片
                output(value["name"], "name")
                if isOutputDebug:
                    output(
                        f"识别耗时：{needTimeStr}s 置信度：{score}\n{textDebug}", "debug")
                output(dataStr, "text")
            except Exception as e:
                tk.messagebox.showerror(
                    '遇到了亿点小问题', f'图片识别异常：\n{value["name"]}\n异常信息：\n{e}')
        # 结束
        endTime = time.time()
        output("\n\n---\n", "none")
        endStr = f"任务结束时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endTime))}\n"
        output(endStr, "text")
        if isOutputDebug:
            endStr = f"任务耗时（秒）：        {endTime-startTime}\n"
            if not allNum == 0:
                endStr += f"单张平均耗时：          {(endTime-startTime)/allNum}\n"
            endStr += f"共计图片数量：          {numOK+numNON+numERR}\n"
            endStr += f"识别正常 的图片数量：    {numOK}\n"
            endStr += f"未识别到文字 的图片数量：{numNON}\n"
            endStr += f"识别失败 的图片数量：    {numERR}\n"
            output(endStr, "debug")
        close()  # 完成后关闭
        self.labelPercentage["text"] = "完成！"
        if isOutputFile:
            if Config.get("isOpenExplorer"):  # 打开输出目录
                os.startfile(outputPath)
            if Config.get("isOpenOutputFile"):  # 打开输出文件
                os.startfile(outputFile)

    def showInstructions(self, e):  # 打开使用说明
        if not self.isRunning == 0:
            tk.messagebox.showwarning(
                '任务进行中', '停止任务后，再打开软件说明')
            return
        self.notebook.select(self.tabFrameOutput)  # 切换到输出选项卡
        outputNow = self.textOutput.get("1.0", tk.END)
        if outputNow and not outputNow == "\n":  # 输出面板内容存在，且不是单换行（初始状态）
            if not tkinter.messagebox.askokcancel('提示', '将清空输出面板。要继续吗？'):
                return
            self.textOutput.delete('1.0', tk.END)
        self.textOutput.insert(tk.END, GetHelpText(ProjectWeb))

    def openProjectWeb(self, e=None):  # 打开项目网页
        webOpen(ProjectWeb)

    def onClose(self):  # 关闭窗口事件
        if self.isRunning == 0:  # 未在运行
            self.win.destroy()  # 直接关闭
        if not self.isRunning == 0:  # 正在运行，需要停止
            self.setRunning(2)
            # self.win.after( # 非阻塞弹出提示框
            #     0, lambda: tk.messagebox.showinfo('请稍候', '等待进程终止，程序稍后将关闭'))
            self.win.after(50, self.waitClose)  # 等待关闭，50ms轮询一次是否已结束子进程

    def waitClose(self):  # 等待进程关闭后销毁窗口
        if self.isRunning == 0:
            self.win.destroy()  # 销毁窗口
        else:
            self.win.after(50, self.waitClose)  # 等待关闭，50ms轮询一次是否已结束子进程


if __name__ == "__main__":
    Win()

# pyinstaller -F -w -i icon/icon.ico -n "Umi-OCR 批量图片转文字" main.py
