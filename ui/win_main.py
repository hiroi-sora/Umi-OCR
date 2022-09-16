from utils.config import Config, Umi  # 最先加载配置
from utils.logger import GetLog
from utils.asset import *  # 资源
from utils.data_structure import KeyList
from ui.win_select_area import IgnoreAreaWin  # 子窗口
from ocr.engine import OCRe, MsnFlag, EngFlag  # 引擎
from ocr.msn_batch_paths import MsnBatch

import os
import time
import keyboard  # 绑定快捷键
from PIL import Image, ImageGrab  # 图像，剪贴板
import tkinter as tk
import tkinter.filedialog
from tkinter import Variable, ttk
from windnd import hook_dropfiles  # 文件拖拽
from pyperclip import copy as pyperclipCopy  # 剪贴板
from webbrowser import open as webOpen  # “关于”面板打开项目网址

TestDict = {}  # 测试接口，用于暴露内部变量给测试器

TempFilePath = "Umi-OCR_temp"
Log = GetLog()


class MainWin:
    def __init__(self):
        self.batList = KeyList()  # 管理批量图片的信息及表格id的列表
        self.tableKeyList = []  # 顺序存放self.imgDict
        self.isRunning = 0  # 0未在运行，1正在运行，2正在停止
        self.lockWidget = []  # 需要运行时锁定的组件

        # 1.初始化主窗口
        self.win = tk.Tk()

        def initWin():
            self.win.title(Umi.name)
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
            # 注册文件拖入，整个主窗口内有效
            hook_dropfiles(self.win, func=self.draggedImages)
        initWin()

        TestDict['MainWin'] = self  # 暴露 self 给测试接口

        # 2.初始化配置项
        Config.initTK(self.win)  # 初始化设置项
        Config.load()  # 加载本地文件

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
            labelUse.bind(
                '<Button-1>', lambda *e: self.showTips(GetHelpText(Umi.website)))  # 绑定鼠标左键点击
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
            self.tabFrameTable = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebook.add(self.tabFrameTable, text=f'{"处理列表": ^10s}')
            # 顶栏
            fr1 = tk.Frame(self.tabFrameTable)
            fr1.pack(side='top', fill='x', pady=2)
            btn = tk.Button(fr1, text=' 浏览 ',  command=self.openFileWin)
            btn.pack(side='left', padx=5)
            self.lockWidget.append(btn)
            tk.Label(fr1, text="或直接拖入").pack(side='left')
            btn = tk.Button(fr1, text='清空', width=8, command=self.clearTable)
            btn.pack(side='right')
            self.lockWidget.append(btn)
            btn = tk.Button(fr1, text='移除', width=8, command=self.delImgList)
            btn.pack(side='right', padx=5)
            self.lockWidget.append(btn)
            # 表格主体
            fr2 = tk.Frame(self.tabFrameTable)
            fr2.pack(side='top', fill='both')
            self.table = ttk.Treeview(
                master=fr2,  # 父容器
                height=50,  # 表格显示的行数,height行
                columns=['name', 'time', 'score'],  # 显示的列
                show='headings',  # 隐藏首列
            )
            # hook_dropfiles(self.table, func=self.draggedImages)  # 注册文件拖入
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

            def initScheduler():  # 计划任务设置
                frameScheduler = tk.LabelFrame(self.optFrame, text="计划任务")
                frameScheduler.pack(side='top', fill='x',
                                    ipady=2, pady=LabelFramePadY, padx=4)

                fr1 = tk.Frame(frameScheduler)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                tk.Checkbutton(fr1, text="完成后打开文件",
                               variable=Config.getTK('isOpenOutputFile')).pack(side='left')
                tk.Checkbutton(fr1, text="完成后打开目录",
                               variable=Config.getTK('isOpenExplorer'),).pack(side='left', padx=15)

                fr2 = tk.Frame(frameScheduler)
                fr2.pack(side='top', fill='x', pady=2, padx=5)
                tk.Checkbutton(fr2, text="本次完成后执行",
                               variable=Config.getTK('isOkMission')).pack(side='left')
                okMissionDict = Config.get("okMission")
                okMissionNameList = [i for i in okMissionDict.keys()]
                wid = ttk.Combobox(fr2, width=10, state="readonly", textvariable=Config.getTK('okMissionName'),
                                   value=okMissionNameList)
                wid.pack(side='left')
                if Config.get("okMissionName") not in okMissionNameList:
                    wid.current(0)  # 初始化Combobox和okMissionName
                labelOpenFile = tk.Label(fr2, text="打开设置文件",
                                         fg="gray", cursor="hand2")
                labelOpenFile.pack(side='right')
                labelOpenFile.bind(
                    '<Button-1>', lambda *e: os.startfile("Umi-OCR_config.json"))
            initScheduler()

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
                                        bg="black", cursor="hand2")
                self.canvas.grid(column=3, row=0, rowspan=10)
                self.canvas.bind(
                    '<Button-1>', lambda *e: self.openSelectArea())
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
                        Config.set("isGlobalHotkey", False)
                        Config.set("globalHotkey", "")
                        tk.messagebox.showwarning("提示",
                                                  f"无法注册快捷键【{hotkey}】\n\n错误信息：\n{err}")

                def updateHotket():  # 刷新快捷键
                    try:
                        keyboard.unhook_all_hotkeys()  # 移除 所有旧快捷键
                    except Exception as err:  # 影响不大。未注册过就调用移除 会报这个异常
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
                wid = tk.Checkbutton(fr1, variable=Config.getTK('isGlobalHotkey'),
                                     text="启用全局快捷键（在其它窗口也可响应）", command=updateHotket)
                wid.grid(column=0, row=0, columnspan=9, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr1, variable=Config.getTK('isNeedCopy'),
                                     text="自动复制识别文本")
                wid.grid(column=0, row=1, columnspan=9, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Button(fr1, text='录制按键',
                                command=readHotkey)
                wid.grid(column=0, row=2, sticky="w")
                self.lockWidget.append(wid)
                tk.Label(fr1, textvariable=Config.getTK('globalHotkey')).grid(
                    column=2, row=2,  sticky="nsew")
                wid = tk.Button(fr1, text='清除', width=8,
                                command=delHotkey)
                wid.grid(column=3, row=2, sticky="w")
                self.lockWidget.append(wid)
                fr1.grid_columnconfigure(2, weight=1)
                fr1.grid_columnconfigure(1, minsize=6)
            initClipboard()

            def initInFile():  # 输入设置
                frameInFile = tk.LabelFrame(self.optFrame, text="输入设置")
                frameInFile.pack(side='top', fill='x',
                                 ipady=2, pady=LabelFramePadY, padx=4)

                fr1 = tk.Frame(frameInFile)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                wid = tk.Checkbutton(
                    fr1, variable=Config.getTK('isRecursiveSearch'), text="递归读取子文件夹中所有图片")
                wid.grid(column=0, row=0, columnspan=2, sticky="w")
                self.lockWidget.append(wid)

                tk.Label(fr1, text="图片后缀：　").grid(column=0, row=2, sticky="w")
                enInSuffix = tk.Entry(
                    fr1, textvariable=Config.getTK('imageSuffix'))
                enInSuffix.grid(column=1, row=2, sticky="nsew")
                self.lockWidget.append(enInSuffix)

                fr1.grid_columnconfigure(1, weight=1)
            initInFile()

            def initOutFile():  # 输出文件设置
                frameOutFile = tk.LabelFrame(self.optFrame, text="输出设置")
                frameOutFile.pack(side='top', fill='x',
                                  ipady=2, pady=LabelFramePadY, padx=4)

                fr1 = tk.Frame(frameOutFile)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                wid = tk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputFile'), text="将识别内容写入本地文件")
                wid.grid(column=0, row=0, columnspan=2, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr1, text="输出调试信息",
                                     variable=Config.getTK('isOutputDebug'))
                wid.grid(column=0, row=1, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr1, text="忽略无文字的图片",
                                     variable=Config.getTK('isIgnoreNoText'),)
                wid.grid(column=1, row=1, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Radiobutton(
                    fr1, text='纯文本.txt文件', value=1, variable=Config.getTK('outputStyle'),)
                wid.grid(column=0, row=3, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Radiobutton(
                    fr1, text='Markdown风格.md文件', value=2, variable=Config.getTK('outputStyle'),)
                wid.grid(column=1, row=3, sticky="w")
                self.lockWidget.append(wid)
                tk.Label(fr1, fg="gray",
                         text="下面两项为空时，默认输出到第一张图片所在的文件夹"
                         ).grid(column=0, row=4, columnspan=2, sticky="nsew")

                fr2 = tk.Frame(frameOutFile)
                fr2.pack(side='top', fill='x', pady=2, padx=5)
                tk.Label(fr2, text="输出目录：").grid(column=0, row=3, sticky="w")
                enOutPath = tk.Entry(
                    fr2, textvariable=Config.getTK('outputFilePath'))
                enOutPath.grid(column=1, row=3,  sticky="nsew")
                self.lockWidget.append(enOutPath)
                fr2.grid_rowconfigure(4, minsize=2)  # 第二行拉开间距
                tk.Label(fr2, text="输出文件名：").grid(column=0, row=5, sticky="w")
                enOutName = tk.Entry(
                    fr2, textvariable=Config.getTK('outputFileName'))
                enOutName.grid(column=1, row=5, sticky="nsew")
                self.lockWidget.append(enOutName)
                fr2.grid_columnconfigure(1, weight=1)  # 第二列自动扩充
            initOutFile()

            def initOcrUI():  # 识别器exe设置
                frameOCR = tk.LabelFrame(
                    self.optFrame, text="OCR识别引擎设置")
                frameOCR.pack(side='top', fill='x', ipady=2,
                              pady=LabelFramePadY, padx=4)
                fr1 = tk.Frame(frameOCR)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                tk.Label(fr1, text="识别语言：　").grid(
                    column=0, row=0, sticky="w")
                ocrConfigDict = Config.get("ocrConfig")
                ocrConfigNameList = [i for i in ocrConfigDict]
                cbox = ttk.Combobox(fr1, width=10, state="readonly", textvariable=Config.getTK('ocrConfigName'),
                                    value=ocrConfigNameList)
                cbox.grid(column=1, row=0,  sticky="nsew")
                if Config.get("ocrConfigName") not in ocrConfigNameList:
                    cbox.current(0)  # 初始化Combobox和ocrConfigName
                self.lockWidget.append(  # 正常状态为特殊值
                    {'widget': cbox, 'stateOFnormal': 'readonly'})
                tk.Label(fr1, text="启动参数：　").grid(
                    column=0, row=2, sticky="w")
                argsStr = tk.Entry(
                    fr1, textvariable=Config.getTK('argsStr'))
                argsStr.grid(column=1, row=2, sticky="nsew")
                self.lockWidget.append(argsStr)

                labelTips = tk.Label(fr1, text="如何添加多国语言？如何调整参数以提高准确度和速度？",
                                     fg="gray", cursor="hand2")
                labelTips.grid(column=0, row=4, columnspan=2, sticky="w")
                labelTips.bind(
                    '<Button-1>', lambda *e: self.showTips(GetHelpConfigText()))  # 绑定鼠标左键点击

                tk.Label(fr1, text="子进程管理：").grid(
                    column=0, row=6, sticky="w")
                ocrRunModeDict = Config.get("ocrRunMode")
                ocrRunModeNameList = [i for i in ocrRunModeDict]
                cboxR = ttk.Combobox(fr1, width=10, state="readonly", textvariable=Config.getTK('ocrRunModeName'),
                                     value=ocrRunModeNameList)
                cboxR.grid(column=1, row=6,  sticky="nsew")
                if Config.get("ocrRunModeName") not in ocrRunModeNameList:
                    cboxR.current(0)  # 初始化Combobox和ocrConfigName
                self.lockWidget.append(  # 正常状态为特殊值
                    {'widget': cboxR, 'stateOFnormal': 'readonly'})

                frState = tk.Frame(fr1)
                frState.grid(column=0, row=7, columnspan=2, sticky="nsew")
                tk.Label(frState, text="子进程状态：").pack(
                    side='left')
                tk.Label(frState, textvariable=Config.getTK('ocrProcessStatus')).pack(
                    side='left')
                labStop = tk.Label(frState, text="强制停止",
                                   cursor="hand2", fg="red")
                labStop.pack(side='right')
                labStart = tk.Label(frState, text="启动", cursor="hand2")
                labStart.pack(side='right', padx=5)
                labStart.bind(
                    '<Button-1>', lambda *e: OCRe.start())
                labStop.bind(
                    '<Button-1>', lambda *e: OCRe.stop())

                fr1.grid_rowconfigure(1, minsize=4)
                fr1.grid_rowconfigure(3, minsize=4)
                fr1.grid_columnconfigure(1, weight=1)
            initOcrUI()

            def initAbout():  # 关于面板
                frameAbout = tk.LabelFrame(
                    self.optFrame, text="关于")
                frameAbout.pack(side='top', fill='x', ipady=2,
                                pady=LabelFramePadY, padx=4)
                tk.Label(frameAbout, image=self.iconImg).pack()  # 图标
                tk.Label(frameAbout, text=Umi.name, fg="gray").pack()
                tk.Label(frameAbout, text=Umi.about, fg="gray").pack()
                labelWeb = tk.Label(frameAbout, text=Umi.website, cursor="hand2",
                                    fg="deeppink")
                labelWeb.pack()  # 文字
                labelWeb.bind(  # 绑定鼠标左键点击，打开网页
                    '<Button-1>', lambda *e: webOpen(Umi.website))
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
            # self.notebook.select(tabFrame)  # 调试用
        initTab3()

        # 4.绑定快捷键
        def bindKey():
            self.win.bind("<Control-V>", self.runClipboard)
        bindKey()

        self.win.mainloop()

    # 加载图片 ===============================================

    def draggedImages(self, paths):  # 拖入图片
        if not self.isRunning == 0:
            tk.messagebox.showwarning(
                '任务进行中', '请停止任务后，再拖入图片')
            return
        self.notebook.select(self.tabFrameTable)  # 切换到表格选项卡
        pathList = []
        for p in paths:  # byte转字符串
            pathList.append(p.decode(Config.sysEncoding,  # 根据系统编码来解码
                            errors='ignore'))
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
            if self.batList.isDataItem('path', path):
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
            self.batList.append(id, dictInfo)

        isRecursiveSearch = Config.get("isRecursiveSearch")
        for path in paths:  # 遍历拖入的所有路径
            if os.path.isdir(path):  # 若是目录
                if isRecursiveSearch:  # 需要递归子文件夹
                    for subDir, dirs, subFiles in os.walk(path):
                        for s in subFiles:
                            addImage(subDir+"\\"+s)
                else:  # 非递归，只搜索子文件夹一层
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
        if not self.batList.isEmpty():
            defaultPath = self.batList.get(index=0)["path"]
        self.win.attributes("-disabled", 1)  # 禁用父窗口
        IgnoreAreaWin(self.closeSelectArea, defaultPath)

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
        areaColor = ["red", "green", "darkorange"]
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
        self.batList.clear()
        chi = self.table.get_children()
        for i in chi:
            self.table.delete(i)  # 表格组件移除

    def delImgList(self):  # 图片列表中删除选中
        if not self.isRunning == 0:
            return
        chi = self.table.selection()
        for i in chi:
            self.table.delete(i)
            self.batList.delete(key=i)

    def setTableItem(self, time, score, key=None, index=-1):  # 改变表中第index项的数据信息
        if not key:
            key = self.batList.indexToKey(index)
        self.table.set(key, column='time', value=time)
        self.table.set(key, column='score', value=score)

    def clearTableItem(self):  # 清空表格数据信息
        keys = self.batList.getKeys()
        for key in keys:  # 清空表格参数
            self.table.set(key, column='time', value="")
            self.table.set(key, column='score', value="")

    # 写字板操作 =============================================

    def textOutputInsert(self, text, position=tk.END):
        self.textOutput.insert(position, text)
        if self.isAutoRoll.get():  # 需要自动滚动
            self.textOutput.see(position)

    # 进行任务 ===============================================

    def setRunning(self, batFlag):  # 设置运行状态。

        def setNone():
            self.btnRun['text'] = '开始任务'
            self.btnRun['state'] = 'normal'
            self.labelPercentage["text"] = "已终止"
            return 'normal'

        def setIniting():
            # self.btnRun['text'] = '正在准备'
            # self.btnRun['state'] = 'disable'
            self.btnRun['text'] = '停止任务'
            self.btnRun['state'] = 'normal'
            self.labelPercentage["text"] = "初始化"
            return 'disable'

        def setRunning():
            self.btnRun['text'] = '停止任务'
            self.btnRun['state'] = 'normal'
            return 'disable'

        def setStopping():
            self.btnRun['text'] = '正在停止'
            self.btnRun['state'] = 'disable'
            return ''

        def setDefault():
            return ''

        state = {
            MsnFlag.none: setNone,
            MsnFlag.initing: setIniting,
            MsnFlag.running: setRunning,
            MsnFlag.stopping: setStopping,
        }.get(batFlag, setDefault)()
        if state:
            for w in self.lockWidget:  # 改变组件状态（禁用，启用）
                if 'widget' in w.keys() and 'stateOFnormal' in w.keys():
                    if state == 'normal':
                        w['widget']['state'] = w['stateOFnormal']  # 正常状态为特殊值
                    else:
                        w['widget']['state'] = state
                else:
                    w['state'] = state
        self.win.update()

    def run(self):
        if OCRe.msnFlag == MsnFlag.none:  # 未在运行
            if self.batList.isEmpty():
                return
            # 创建输出文件
            if Config.get('isOutputFile'):
                suffix = '.txt' if Config.get('outputStyle') == 1 else '.md'
                outPath = Config.get('outputFilePath') + \
                    '\\' + Config.get('outputFileName')+suffix
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
            # 锁定UI
            # self.setRunning(MsnFlag.initing)
            # 初始化文本处理器
            tb = MsnBatch(self, self.batList, self.setTableItem,
                          self.textOutputInsert, self.setRunning,
                          self.clearTableItem)
            # 开始运行
            paths = self.batList.getItemValueList('path')
            OCRe.runMission(paths,
                            onStart=tb.onStart, onGet=tb.onGet,
                            onStop=tb.onStop, onError=tb.onError,
                            winSetMsnFlag=self.setRunning)
        # 允许任务进行中或初始化的中途停止任务
        elif OCRe.msnFlag == MsnFlag.running or OCRe.msnFlag == MsnFlag.initing:
            OCRe.stopByMode()

    def onClose(self):  # 关闭窗口事件
        OCRe.stop()  # 强制关闭引擎进程，加快子线程结束
        if OCRe.engFlag == EngFlag.none and OCRe.msnFlag == MsnFlag.none:  # 未在运行
            self.win.destroy()  # 直接关闭
        else:
            self.win.after(50, self.waitClose)  # 等待关闭，50ms轮询一次是否已结束子线程

    def waitClose(self):  # 等待线程关闭后销毁窗口
        Log.info(f'关闭中，等待 {OCRe.engFlag} | {OCRe.msnFlag}')
        if OCRe.engFlag == EngFlag.none and OCRe.msnFlag == MsnFlag.none:  # 未在运行
            self.win.destroy()  # 销毁窗口
            Log.info(f'主窗 exit =====================')
            exit(0)
        else:
            self.win.after(50, self.waitClose)  # 等待关闭，50ms轮询一次是否已结束子进程

    def showTips(self, tipsText):  # 显示提示
        if not self.isRunning == 0:
            tk.messagebox.showwarning(
                '任务进行中', '请停止任务后，再打开软件说明')
            return
        self.notebook.select(self.tabFrameOutput)  # 切换到输出选项卡
        outputNow = self.textOutput.get("1.0", tk.END)
        if outputNow and not outputNow == "\n":  # 输出面板内容存在，且不是单换行（初始状态）
            if not tkinter.messagebox.askokcancel('提示', '将清空输出面板。要继续吗？'):
                return
            self.textOutput.delete('1.0', tk.END)
        self.textOutput.insert(tk.END, tipsText)
