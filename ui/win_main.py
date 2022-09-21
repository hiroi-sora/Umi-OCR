from utils.config import Config, Umi  # 最先加载配置
from utils.logger import GetLog
from utils.asset import *  # 资源
from utils.data_structure import KeyList
from utils.tool import Tool
from ui.win_screenshot import ScreenshotWin  # 截屏
from ui.win_select_area import IgnoreAreaWin  # 子窗口
from ui.widget import Widget  # 控件
from ui.pmw.PmwBalloon import Balloon  # 气泡提示
from ocr.engine import OCRe, MsnFlag, EngFlag  # 引擎
# 识图任务处理器
from ocr.msn_batch_paths import MsnBatch
from ocr.msn_quick import MsnQuick

import os
import time
from PIL import Image  # 图像
import tkinter as tk
import tkinter.filedialog
from tkinter import Variable, ttk
from windnd import hook_dropfiles  # 文件拖拽
from webbrowser import open as webOpen  # “关于”面板打开项目网址

TempFilePath = "Umi-OCR_temp"
Log = GetLog()


class MainWin:
    def __init__(self):
        self.batList = KeyList()  # 管理批量图片的信息及表格id的列表
        self.tableKeyList = []  # 顺序存放self.imgDict
        self.lockWidget = []  # 需要运行时锁定的组件

        # 1.初始化主窗口
        self.win = tk.Tk()
        self.balloon = Balloon(self.win)  # 气泡框

        def initWin():
            self.win.title(Umi.name)
            # 窗口大小与位置
            w, h = 360, 500  # 窗口初始大小与最小大小
            ws, hs = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            x, y = round(ws/2 - w/2), round(hs/2 - h/2)  # 初始位置，屏幕正中
            self.win.minsize(w, h)  # 最小大小
            self.win.geometry(f"{w}x{h}+{x}+{y}")  # 初始大小与位置
            self.win.protocol("WM_DELETE_WINDOW", self.onClose)  # 窗口关闭
            # 注册文件拖入，整个主窗口内有效
            hook_dropfiles(self.win, func=self.draggedImages)
            # 图标
            # Asset.initRelease()  # 释放base64资源到本地
            Asset.initTK()  # 初始化tk图片
            self.win.iconphoto(False, Asset.getImgTK('umiocr64'))  # 设置窗口图标
        initWin()

        # 2.初始化配置项
        Config.initTK(self)  # 初始化设置项
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
            self.balloon.bind(self.btnRun, '开始任务')
            # 左侧文本和进度条
            vFrame2 = tk.Frame(fr)
            vFrame2.pack(side='top', fill='x')
            # labelUse = tk.Label(vFrame2, text="使用说明",
            #                     fg="gray", cursor="hand2")
            # labelUse.pack(side='left', padx=5)
            # labelUse.bind(
            #     '<Button-1>', lambda *e: self.showTips(GetHelpText(Umi.website)))  # 绑定鼠标左键点击
            # 进度条上方的两个label
            tk.Label(vFrame2, textvariable=Config.getTK('tipsTop2')).pack(
                side='right', padx=2)
            tk.Label(vFrame2, textvariable=Config.getTK('tipsTop1')).pack(
                side='right', padx=2)
            self.progressbar = ttk.Progressbar(fr)
            self.progressbar.pack(side='top', padx=5, fill="x")
        initTop()

        self.notebook = ttk.Notebook(self.win)  # 初始化选项卡组件
        self.notebook.pack(expand=True, fill=tk.BOTH)  # 填满父组件
        self.notebookTab = []

        def initTab1():  # 表格卡
            tabFrameTable = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebookTab.append(tabFrameTable)
            self.notebook.add(tabFrameTable, text=f'{"处理列表": ^10s}')
            # 顶栏
            fr1 = tk.Frame(tabFrameTable)
            fr1.pack(side='top', fill='x', padx=1, pady=1)
            # 左
            btn = tk.Button(fr1, image=Asset.getImgTK('screenshot24'),  # 截图按钮
                            command=self.openScreenshot,
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '屏幕截图')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            btn = tk.Button(fr1, image=Asset.getImgTK('paste24'),  # 剪贴板按钮
                            command=self.runClipboard,
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '读取剪贴板')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            # tk.Label(fr1, text="或直接拖入").pack(side='left')
            # 右
            btn = tk.Button(fr1, image=Asset.getImgTK('clear24'),  # 清空按钮
                            command=self.clearTable,
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '清空表格')
            btn.pack(side='right')
            self.lockWidget.append(btn)
            btn = tk.Button(fr1, image=Asset.getImgTK('delete24'),  # 删除按钮
                            command=self.delImgList,
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '移除选中的条目\nShift+左键 可选中多个条目')
            btn.pack(side='right')
            self.lockWidget.append(btn)
            btn = tk.Button(fr1, image=Asset.getImgTK('openfile24'),  # 打开文件按钮
                            command=self.openFileWin,
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '浏览文件')
            btn.pack(side='right', padx=5)
            self.lockWidget.append(btn)
            # 表格主体
            fr2 = tk.Frame(tabFrameTable)
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
            tabFrameOutput = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebookTab.append(tabFrameOutput)
            self.notebook.add(tabFrameOutput, text=f'{"识别内容": ^10s}')
            fr1 = tk.Frame(tabFrameOutput)
            fr1.pack(side='top', fill='x', padx=1, pady=1)
            self.isAutoRoll = tk.IntVar()
            self.isAutoRoll.set(1)
            # 左
            btn = tk.Button(fr1, image=Asset.getImgTK('screenshot24'),  # 截图按钮
                            command=self.openScreenshot,
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '屏幕截图')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            btn = tk.Button(fr1, image=Asset.getImgTK('paste24'),  # 剪贴板按钮
                            command=self.runClipboard,
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '读取剪贴板')
            btn.pack(side='left')
            self.lockWidget.append(btn)

            # 右
            btn = tk.Button(fr1, image=Asset.getImgTK('clear24'),  # 清空按钮
                            command=lambda: self.textOutput.delete(
                                '1.0', tk.END),
                            width=48, bg='white', relief='groove', overrelief='ridge',)
            self.balloon.bind(btn, '清空输出面板')
            btn.pack(side='right')

            tk.Checkbutton(fr1, variable=self.isAutoRoll, text="自动滚动").pack(
                side='right', padx=20)

            fr2 = tk.Frame(tabFrameOutput)
            fr2.pack(side='top', fill='both')
            vbar = tk.Scrollbar(fr2, orient='vertical')  # 滚动条
            vbar.pack(side="right", fill='y')
            self.textOutput = tk.Text(fr2, height=500, width=500)
            self.textOutput.pack(fill='both', side="left")
            vbar["command"] = self.textOutput.yview
            self.textOutput["yscrollcommand"] = vbar.set
            Config.set('panelOutput', self.panelOutput)
        initTab2()

        def initTab3():  # 设置卡
            tabFrameConfig = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebookTab.append(tabFrameConfig)
            self.notebook.add(tabFrameConfig, text=f'{"设置": ^10s}')

            def initOptFrame():  # 初始化可滚动画布 及 内嵌框架
                optVbar = tk.Scrollbar(
                    tabFrameConfig, orient="vertical")  # 创建滚动条
                optVbar.pack(side="right", fill="y")
                self.optCanvas = tk.Canvas(
                    tabFrameConfig, highlightthickness=0)  # 创建画布，用于承载框架。highlightthickness取消高亮边框
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
                wid.unbind_class("TCombobox", "<MouseWheel>")  # 解绑默认滚轮事件，防止误触
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

            def quickOCR():  # 快捷识图设置
                quickLabel = tk.LabelFrame(
                    self.optFrame, text='快捷识图')
                quickLabel.pack(side='top', fill='x',
                                ipady=2, pady=LabelFramePadY, padx=4)
                Widget.hotkeyFrame(quickLabel, '截图识别', 'Clipboard',
                                   self.openScreenshot).pack(side='top', fill='x', padx=4)
                Widget.hotkeyFrame(quickLabel, '读剪贴板', 'Screenshot',
                                   self.runClipboard).pack(side='top', fill='x', padx=4)
                tk.Checkbutton(quickLabel, variable=Config.getTK('isNeedCopy'),
                               text='复制识别出的文字').pack(side='left', fill='x', padx=4)
            quickOCR()

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
                # 输出文件类型勾选
                fr1 = tk.Frame(frameOutFile)
                fr1.pack(side='top', fill='x', pady=2, padx=5)

                def offAllOutput(e):  # 关闭全部输出
                    if OCRe.msnFlag == MsnFlag.none:
                        Config.set('isOutputTxt', False)
                        Config.set('isOutputMD', False)
                labelOff = tk.Label(fr1, text='关闭本地输出', cursor="hand2")
                labelOff.grid(column=0, row=0, sticky="w")
                labelOff.bind('<Button-1>', offAllOutput)  # 绑定关闭全部输出
                wid = tk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputJsonl'), text="分行.jsonl文件")
                wid.grid(column=1, row=0,  sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputTxt'), text="纯文本.txt文件　")
                wid.grid(column=0, row=1,  sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputMD'), text="图文链接.md文件")
                wid.grid(column=1, row=1,  sticky="w")
                self.lockWidget.append(wid)

                tk.Label(frameOutFile, fg="gray",
                         text="下面两项为空时，默认输出到第一张图片所在的文件夹"
                         ).pack(side='top', fill='x', padx=5)
                # 输出目录
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
                # 其它选项
                fr3 = tk.Frame(frameOutFile)
                fr3.pack(side='top', fill='x', pady=2, padx=5)
                wid = tk.Checkbutton(fr3, text="输出调试信息　",
                                     variable=Config.getTK('isOutputDebug'))
                wid.grid(column=0, row=0, sticky="w")
                self.lockWidget.append(wid)
                wid = tk.Checkbutton(fr3, text="忽略无文字的图片",
                                     variable=Config.getTK('isIgnoreNoText'),)
                wid.grid(column=1, row=0, sticky="w")
                self.lockWidget.append(wid)
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
                cbox.unbind_class("TCombobox", "<MouseWheel>")  # 解绑默认滚轮事件，防止误触
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

                tk.Label(fr1, text="引擎管理策略：").grid(
                    column=0, row=6, sticky="w")
                ocrRunModeDict = Config.get("ocrRunMode")
                ocrRunModeNameList = [i for i in ocrRunModeDict]
                cboxR = ttk.Combobox(fr1, width=10, state="readonly", textvariable=Config.getTK('ocrRunModeName'),
                                     value=ocrRunModeNameList)
                cboxR.unbind_class(
                    "TCombobox", "<MouseWheel>")  # 解绑默认滚轮事件，防止误触
                cboxR.grid(column=1, row=6,  sticky="nsew")
                if Config.get("ocrRunModeName") not in ocrRunModeNameList:
                    cboxR.current(0)  # 初始化Combobox和ocrConfigName
                self.lockWidget.append(  # 正常状态为特殊值
                    {'widget': cboxR, 'stateOFnormal': 'readonly'})

                frState = tk.Frame(fr1)
                frState.grid(column=0, row=7, columnspan=2, sticky="nsew")
                tk.Label(frState, text="引擎当前状态：").pack(
                    side='left')
                tk.Label(frState, textvariable=Config.getTK('ocrProcessStatus')).pack(
                    side='left')
                labStop = tk.Label(frState, text="停止",
                                   cursor="hand2", fg="red")
                labStop.pack(side='right')
                self.balloon.bind(labStop, '强制停止引擎进程')
                labStart = tk.Label(frState, text="启动", cursor="hand2")
                labStart.pack(side='right', padx=5)

                def engStart():
                    try:
                        OCRe.start()
                    except Exception as err:
                        tk.messagebox.showerror(
                            '遇到了亿点小问题',
                            f'引擎启动失败：{err}')
                labStart.bind(
                    '<Button-1>', lambda *e: engStart())
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
                tk.Label(frameAbout, image=Asset.getImgTK(
                    'umiocr64')).pack()  # 图标
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
        initTab3()

        self.win.mainloop()

    # 加载图片 ===============================================

    def draggedImages(self, paths):  # 拖入图片
        if not OCRe.msnFlag == MsnFlag.none:
            tk.messagebox.showwarning(
                '任务进行中', '请停止任务后，再拖入图片')
            return
        self.notebook.select(self.notebookTab[0])  # 切换到表格选项卡
        pathList = []
        for p in paths:  # byte转字符串
            pathList.append(p.decode(Config.sysEncoding,  # 根据系统编码来解码
                            errors='ignore'))
        self.addImagesList(pathList)

    def openFileWin(self):  # 打开选择文件窗
        if not OCRe.msnFlag == MsnFlag.none:
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

    # 忽略区域 ===============================================

    def openSelectArea(self):  # 打开选择区域
        if not OCRe.msnFlag == MsnFlag.none:
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
        if not OCRe.msnFlag == MsnFlag.none:
            return
        self.progressbar["value"] = 0
        Config.set('tipsTop1', '')
        Config.set('tipsTop2', '请导入文件')
        Config.set("outputFilePath", "")
        Config.set("outputFileName", "")
        self.batList.clear()
        chi = self.table.get_children()
        for i in chi:
            self.table.delete(i)  # 表格组件移除

    def delImgList(self):  # 图片列表中删除选中
        if not OCRe.msnFlag == MsnFlag.none:
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

    def panelOutput(self, text, position=tk.END):
        self.textOutput.insert(position, text)
        if self.isAutoRoll.get():  # 需要自动滚动
            self.textOutput.see(position)

    # 窗口操作 =============================================

    def gotoTop(self):  # 主窗置顶
        if self.win.state() == "iconic":  # 窗口最小化状态下
            self.win.state("normal")  # 恢复前台状态
        self.win.attributes('-topmost', 1)  # 设置层级最前
        self.win.attributes('-topmost', 0)  # 然后立刻解除

    # 进行任务 ===============================================

    def setRunning(self, batFlag):  # 设置运行状态。

        def setNone():
            self.btnRun['text'] = '开始任务'
            self.btnRun['state'] = 'normal'
            Config.set('tipsTop2', '已结束')
            return 'normal'

        def initing():
            self.btnRun['text'] = '停止任务'
            self.btnRun['state'] = 'normal'
            Config.set('tipsTop2', '初始化')
            self.progressbar["maximum"] = 50  # 重置进度条长度，值越小加载动画越快
            self.progressbar['mode'] = 'indeterminate'  # 进度条为来回动模式
            self.progressbar.start()  # 进度条开始加载动画
            return 'disable'

        def running():
            self.progressbar.stop()  # 进度条停止加载动画
            self.progressbar['mode'] = 'determinate'  # 进度条静止模式
            return ''

        def stopping():
            self.btnRun['text'] = '正在停止'
            self.btnRun['state'] = 'disable'
            if str(self.progressbar["mode"]) == 'indeterminate':
                self.progressbar.stop()  # 进度条停止加载动画
                self.progressbar['mode'] = 'determinate'  # 进度条静止模式
            return ''

        state = {
            MsnFlag.none: setNone,
            MsnFlag.initing: initing,
            MsnFlag.running: running,
            MsnFlag.stopping: stopping,
        }.get(batFlag, '')()
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

    def run(self):  # 运行按钮触发
        if OCRe.msnFlag == MsnFlag.none:  # 未在运行
            if self.batList.isEmpty():
                return
            # 初始化文本处理器
            try:
                msnBat = MsnBatch()
            except Exception as err:
                tk.messagebox.showwarning('遇到了亿点小问题', f'{err}')
                return  # 未开始运行，终止本次运行
            # 开始运行
            paths = self.batList.getItemValueList('path')
            OCRe.runMission(paths, msnBat)
        # 允许任务进行中或初始化的中途停止任务
        elif OCRe.msnFlag == MsnFlag.running or OCRe.msnFlag == MsnFlag.initing:
            OCRe.stopByMode()

    def runClipboard(self, e=None):  # 识别剪贴板
        if not OCRe.msnFlag == MsnFlag.none:  # 正在运行，不执行
            return
        clipData = Tool.getClipboardFormat()  # 读取剪贴板

        # 剪贴板中是位图（优先）
        if isinstance(clipData, int):
            try:  # 初始化快捷识图任务处理器
                msnQui = MsnQuick()
            except Exception as err:
                tk.messagebox.showwarning('遇到了亿点小问题', f'{err}')
                return  # 未开始运行，终止本次运行
            # 开始运行
            OCRe.runMission(['clipboard'], msnQui)
            self.notebook.select(self.notebookTab[1])  # 转到输出卡
            self.gotoTop()  # 主窗置顶

        # 剪贴板中是文件列表（文件管理器中对着文件ctrl+c得到句柄）
        elif isinstance(clipData, tuple):
            # 检验文件列表中是否存在合法文件类型
            suf = Config.get("imageSuffix").split()  # 许可后缀列表
            flag = False
            for path in clipData:  # 检验文件列表中是否存在许可后缀
                if suf and os.path.splitext(path)[1].lower() in suf:
                    flag = True
                    break
            # 存在，则将文件载入主表并执行任务
            if flag:
                self.notebook.select(self.notebookTab[0])  # 转到主表卡
                self.gotoTop()  # 主窗置顶
                self.clearTable()  # 清空主表
                self.addImagesList(clipData)  # 添加到主表
                self.run()  # 开始任务任务

        else:
            self.panelOutput('剪贴板中未查询到图片信息\n')

    def openScreenshot(self, e=None):  # 打开截图窗口
        # try:
        ScreenshotWin(self.closeScreenshot)
        # except Exception as err:
        #     self.panelOutput(f'截图失败：{err}')

    def closeScreenshot(self, flag):  # 关闭截图窗口，返回T表示已复制到剪贴板
        if flag:  # 成功
            self.runClipboard()  # 剪贴板识图

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
        if not OCRe.msnFlag == MsnFlag.none:
            tk.messagebox.showwarning(
                '任务进行中', '请停止任务后，再打开软件说明')
            return
        self.notebook.select(self.notebookTab[1])  # 切换到输出选项卡
        outputNow = self.textOutput.get("1.0", tk.END)
        if outputNow and not outputNow == "\n":  # 输出面板内容存在，且不是单换行（初始状态）
            if not tkinter.messagebox.askokcancel('提示', '将清空输出面板。要继续吗？'):
                return
            self.textOutput.delete('1.0', tk.END)
        self.textOutput.insert(tk.END, tipsText)

# 全角空格：【　】
