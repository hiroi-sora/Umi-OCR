from utils.config import Config, Umi, ScsModeFlag, WindowTopModeFlag  # 最先加载配置
from utils.logger import GetLog
from utils.asset import *  # 资源
from utils.data_structure import KeyList
from utils.tool import Tool
from utils.startup import Startup  # 启动方式
from utils.hotkey import Hotkey  # 快捷键
from ui.win_screenshot import ScreenshotCopy  # 截屏
from ui.win_select_area import IgnoreAreaWin  # 子窗口
from ui.win_ocr_language import ChangeOcrLanguage  # 更改语言
from ui.widget import Widget  # 控件
from ui.pmw.PmwBalloon import Balloon  # 气泡提示
from ui.tray import SysTray
from ocr.engine import OCRe, MsnFlag, EngFlag  # 引擎
# 识图任务处理器
from ocr.msn_batch_paths import MsnBatch
from ocr.msn_quick import MsnQuick

import os
import ctypes
from PIL import Image  # 图像
import tkinter as tk
import tkinter.font
import tkinter.filedialog
import tkinter.colorchooser
from tkinter import ttk
from windnd import hook_dropfiles  # 文件拖拽
from webbrowser import open as webOpen  # “关于”面板打开项目网址
from argparse import ArgumentParser  # 启动参数

Log = GetLog()


class MainWin:
    def __init__(self):
        self.batList = KeyList()  # 管理批量图片的信息及表格id的列表
        self.tableKeyList = []  # 顺序存放self.imgDict
        self.lockWidget = []  # 需要运行时锁定的组件

        # 1.初始化主窗口
        self.win = tk.Tk()
        self.win.withdraw()  # 隐藏窗口，等初始化完毕再考虑是否显示
        self.balloon = Balloon(self.win)  # 气泡框

        def initStyle():  # 初始化样式
            style = ttk.Style()
            # winnative clam alt default classic vista xpnative
            # style.theme_use('default')
            style.configure('icon.TButton', padding=(12, 0))
            style.configure('go.TButton', font=('Microsoft YaHei', '12', ''),  # bold
                            width=9)
            style.configure('gray.TCheckbutton', foreground='gray')
        initStyle()

        def initDPI():
            # 调用api设置成由应用程序缩放
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            # 调用api获得当前的缩放因子
            ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            # 设置缩放因子
            self.win.tk.call('tk', 'scaling', ScaleFactor/100)
        # initDPI()

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
            Asset.initRelease()  # 释放base64资源到本地
            Asset.initTK()  # 初始化tk图片
            self.win.iconphoto(False, Asset.getImgTK('umiocr24'))  # 设置窗口图标
        initWin()

        # 2.初始化配置项
        Config.initTK(self)  # 初始化设置项
        Config.load()  # 加载本地文件
        Config.checkMultiOpen()  # 检查多开

        # 3.初始化组件
        def initTop():  # 顶部按钮
            tk.Frame(self.win, height=5).pack(side='top')
            fr = tk.Frame(self.win)
            fr.pack(side='top', fill="x", padx=5)
            # 右侧按钮
            self.btnRun = ttk.Button(fr, command=self.run, text='开始任务',
                                     style='go.TButton')
            self.btnRun.pack(side='right', fill='y')
            # 左侧文本和进度条
            vFrame2 = tk.Frame(fr)
            vFrame2.pack(side='top', fill='x')
            # 进度条上方
            wid = ttk.Checkbutton(vFrame2, variable=Config.getTK('isWindowTop'),
                                  text='窗口置顶', style='gray.TCheckbutton')
            wid.pack(side='left')
            self.balloon.bind(
                wid, '窗口锁定于系统顶层\n\n启用后，软件内的鼠标悬停提示框会被隐藏')
            tk.Label(vFrame2, textvariable=Config.getTK('tipsTop2')).pack(
                side='right', padx=2)
            tk.Label(vFrame2, textvariable=Config.getTK('tipsTop1')).pack(
                side='right', padx=2)
            self.progressbar = ttk.Progressbar(fr)
            self.progressbar.pack(side='top', padx=2, pady=2, fill="x")
        initTop()

        self.notebook = ttk.Notebook(self.win)  # 初始化选项卡组件
        self.notebook.pack(expand=True, fill=tk.BOTH)  # 填满父组件
        self.notebookTab = []

        def initTab1():  # 表格卡
            tabFrameTable = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebookTab.append(tabFrameTable)
            self.notebook.add(tabFrameTable, text=f'{"批量处理": ^10s}')
            # 顶栏
            fr1 = tk.Frame(tabFrameTable)
            fr1.pack(side='top', fill='x', padx=1, pady=1)
            # 左
            btn = ttk.Button(fr1, image=Asset.getImgTK('screenshot24'),  # 截图按钮
                             command=self.openScreenshot,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(
                btn, '屏幕截图　　说明\n左键拖拽：框选区域\n右键点击：取消框选\n　　 Esc：退出截图')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            btn = ttk.Button(fr1, image=Asset.getImgTK('paste24'),  # 剪贴板按钮
                             command=self.runClipboard,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(btn, '粘贴图片')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            btn = ttk.Button(fr1, image=Asset.getImgTK('language24'),  # 语言按钮
                             command=ChangeOcrLanguage,
                             style='icon.TButton',  takefocus=0)
            self.balloon.bind(btn, '更改OCR语言')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            # 右
            btn = ttk.Button(fr1, image=Asset.getImgTK('clear24'),  # 清空按钮
                             command=self.clearTable,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(btn, '清空表格')
            btn.pack(side='right')
            self.lockWidget.append(btn)
            btn = ttk.Button(fr1, image=Asset.getImgTK('delete24'),  # 删除按钮
                             command=self.delImgList,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(btn, '移除选中的文件\n按住Shift或Ctrl，点击左键可选中多个文件')
            btn.pack(side='right')
            self.lockWidget.append(btn)
            btn = ttk.Button(fr1, image=Asset.getImgTK('openfile24'),  # 打开文件按钮
                             command=self.openFileWin,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(btn, '浏览文件')
            btn.pack(side='right')
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
            btn = ttk.Button(fr1, image=Asset.getImgTK('screenshot24'),  # 截图按钮
                             command=self.openScreenshot,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(
                btn, '屏幕截图　　说明\n左键拖拽：框选区域\n右键点击：取消框选\n　　 Esc：退出截图')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            btn = ttk.Button(fr1, image=Asset.getImgTK('paste24'),  # 剪贴板按钮
                             command=self.runClipboard,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(btn, '粘贴图片')
            btn.pack(side='left')
            self.lockWidget.append(btn)
            btn = ttk.Button(fr1, image=Asset.getImgTK('language24'),  # 语言按钮
                             command=ChangeOcrLanguage,
                             style='icon.TButton',  takefocus=0)
            self.balloon.bind(btn, '更改OCR语言')
            btn.pack(side='left')
            self.lockWidget.append(btn)

            # 右
            btn = ttk.Button(fr1, image=Asset.getImgTK('clear24'),  # 清空按钮
                             command=self.panelClear,
                             style='icon.TButton',  takefocus=0,)
            self.balloon.bind(btn, '清空输出面板\n在【设置→快捷识图】可启用自动清空面板')
            btn.pack(side='right')

            ttk.Checkbutton(fr1, variable=self.isAutoRoll, text="自动滚动",
                            takefocus=0,).pack(side='right')
            tf = tk.Label(fr1, text='字体', fg='gray', cursor='hand2')
            tf.pack(side='right', padx=10)
            tf.bind(
                '<Button-1>', lambda *e: self.notebook.select(self.notebookTab[2]))  # 转到设置卡
            self.balloon.bind(tf, '在【设置】选项卡更改输出面板的字体')

            fr2 = tk.Frame(tabFrameOutput)
            fr2.pack(side='top', fill='both')
            vbar = tk.Scrollbar(fr2, orient='vertical')  # 滚动条
            vbar.pack(side="right", fill='y')
            self.textOutput = tk.Text(fr2, height=500, width=500)
            self.textOutput.pack(fill='both', side="left")
            self.textOutput.tag_config(  # 添加标签
                'blue', foreground='blue')
            vbar["command"] = self.textOutput.yview
            self.textOutput["yscrollcommand"] = vbar.set
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

            def initTopTips():  # 顶部提示
                fTips = tk.Frame(self.optFrame)
                fTips.pack(side='top')
                tipsLab = tk.Label(
                    fTips, fg='red',
                    text='关闭窗口置顶，方可显示鼠标悬停提示框')
                if Config.get('isWindowTop'):
                    tipsLab.pack(side='top')
                tk.Frame(fTips).pack(side='top')  # 空框架，用于自动调整高度的占位

                def changeWinTopMode():  # 改变窗口置顶【模式】事件
                    Config.set('isWindowTop',
                               Config.get('WindowTopMode') == WindowTopModeFlag.eternity)
                Config.addTrace('WindowTopMode', changeWinTopMode)
                changeWinTopMode()  # 初始化

                def changeWinTopIS():  # 改变窗口置顶【标志】事件
                    Config.set('WindowTopMode',  # 改变窗口置顶模式
                               WindowTopModeFlag.eternity if Config.get('isWindowTop') else WindowTopModeFlag.finish)
                    self.gotoTop()
                    if Config.get('isWindowTop'):  # 切换到置顶
                        tipsLab.pack(side='top')
                    else:
                        tipsLab.pack_forget()
                    # 不刷新框架，而是在尾部预留空间来容纳高度变化
                    # self.updateFrameHeight()  # 刷新框架
                Config.addTrace('isWindowTop', changeWinTopIS)
                # 以上两个事件互相调用不会造成无限递归，因为配置项被修改同步后，第二次set不会再调用跟踪事件。
            initTopTips()

            def initSoftwareFrame():  # 软件行为设置
                fSoft = tk.LabelFrame(
                    self.optFrame, text='通用设置')
                fSoft.pack(side='top', fill='x',
                           ipady=2, pady=LabelFramePadY, padx=4)

                # 主面板字体设置
                fr3 = tk.Frame(fSoft)
                fr3.pack(side='top', fill='x', pady=2, padx=5)
                fr3.grid_columnconfigure(1, weight=1)
                self.balloon.bind(fr3, '调整【识别内容】选项卡中输出面板的字体样式')
                tk.Label(fr3, text='输出面板字体').grid(column=0, row=0, sticky='w')
                ff = tk.font.families()  # 获取系统字体
                fontFamilies = []
                fontFamiliesABC = []
                for i in ff:
                    if not i[0] == '@':  # 排除竖版
                        if '\u4e00' <= i[0] <= '\u9fff':  # 中文开头的优先
                            fontFamilies.append(i)
                        else:
                            fontFamiliesABC.append(i)
                fontFamilies += fontFamiliesABC
                cbox = ttk.Combobox(fr3, state='readonly', takefocus=0,
                                    textvariable=Config.getTK('textpanelFontFamily'), value=fontFamilies)
                cbox.grid(column=1, row=0, sticky='ew')
                self.balloon.bind(cbox, '不要使用滚轮。\n请用上下方向键或拉动滚动条来浏览列表')
                tk.Label(fr3, text='字号').grid(column=2, row=0, sticky='w')
                tk.Entry(fr3, textvariable=Config.getTK('textpanelFontSize'),
                         width=4, takefocus=0).grid(column=3, row=0, sticky='w')
                tk.Label(fr3, text=' ').grid(column=4, row=0, sticky='w')
                ttk.Checkbutton(fr3, text='加粗',
                                variable=Config.getTK('isTextpanelFontBold')).grid(column=5, row=0, sticky='w')
                # 检查当前配置字体是否存在
                f = Config.get('textpanelFontFamily')
                if f and f not in fontFamilies:
                    Log.error(f'配置输出面板字体【{f}】不存在。重置为空')
                    Config.set('textpanelFontFamily', '')

                def updateTextpanel():
                    f = Config.get('textpanelFontFamily')
                    s = Config.get('textpanelFontSize')
                    b = Config.get('isTextpanelFontBold')
                    font = (f, s, 'bold' if b else 'normal')
                    self.textOutput['font'] = font
                Config.addTrace('textpanelFontFamily', updateTextpanel)
                Config.addTrace('textpanelFontSize', updateTextpanel)
                Config.addTrace('isTextpanelFontBold', updateTextpanel)
                updateTextpanel()

                fr1 = tk.Frame(fSoft)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                fr1.grid_columnconfigure(1, weight=1)
                self.balloon.bind(
                    fr1, '可关闭/开启系统托盘图标，修改双击图标时触发的功能\n该项目修改后，下次打开软件生效')
                wid = ttk.Checkbutton(fr1, text='显示系统托盘图标',
                                      variable=Config.getTK('isTray'))
                wid.grid(column=0, row=0, sticky='w')
                Widget.comboboxFrame(fr1, '，双击图标', 'clickTrayMode', width=12).grid(
                    column=1, row=0, sticky='w')

                fr2 = tk.Frame(fSoft)
                fr2.pack(side='top', fill='x', pady=2, padx=5)
                self.balloon.bind(fr2, '不显示系统托盘图标时，关闭面板会退出软件')
                tk.Label(fr2, text='窗口关闭：').pack(side='left', padx=2)
                ttk.Radiobutton(fr2, text='最小化到托盘',
                                variable=Config.getTK('isBackground'), value=True).pack(side='left')
                ttk.Radiobutton(fr2, text='退出软件',
                                variable=Config.getTK('isBackground'), value=False).pack(side='left', padx=15)

                # 弹出方式设置
                fr3 = tk.Frame(fSoft)
                fr3.pack(side='top', fill='x', pady=2, padx=5)
                tk.Label(fr3, text='窗口置顶：').pack(side='left', padx=2)
                wid = ttk.Radiobutton(fr3, text='自动弹出',
                                      variable=Config.getTK('WindowTopMode'), value=WindowTopModeFlag.finish)
                wid.pack(side='left')
                self.balloon.bind(
                    wid, '当主窗口处于后台，\n唤起快捷识图、或批量任务完成时弹出')
                wid = ttk.Radiobutton(fr3, text='始终置顶',
                                      variable=Config.getTK('WindowTopMode'), value=WindowTopModeFlag.eternity)
                wid.pack(side='left', padx=5)
                self.balloon.bind(
                    wid, '窗口锁定于系统顶层\n\n启用后，软件内的鼠标悬停提示框会被隐藏')
                wid = ttk.Radiobutton(fr3, text='不要弹出',
                                      variable=Config.getTK('WindowTopMode'), value=WindowTopModeFlag.never)
                wid.pack(side='left')
                self.balloon.bind(
                    wid, '不会主动弹出窗口')

                # 启动方式设置
                fr4 = tk.Frame(fSoft)
                fr4.pack(side='top', fill='x', pady=2, padx=5)
                self.balloon.bind(
                    fr4, '可设置静默启动，收纳到系统托盘，不显示主窗口')
                ttk.Checkbutton(fr4, variable=Config.getTK('isAutoStartup'),
                                text='开机自启', command=Startup.switchAutoStartup).pack(side='left')
                ttk.Checkbutton(fr4, variable=Config.getTK('isStartMenu'),
                                text='开始菜单项', command=Startup.switchStartMenu).pack(side='left', padx=20)
                ttk.Checkbutton(fr4, variable=Config.getTK('isDesktop'),
                                text='桌面快捷方式', command=Startup.switchDesktop).pack(side='left')
            initSoftwareFrame()

            def quickOCR():  # 快捷识图设置
                fQuick = tk.LabelFrame(
                    self.optFrame, text='快捷识图')
                fQuick.pack(side='top', fill='x',
                            ipady=2, pady=LabelFramePadY, padx=4)
                # 截图快捷键触发时，子线程向主线程发送事件，在主线程中启动截图窗口
                # 避免子线程直接唤起截图窗导致的窗口闪烁现象
                self.win.bind('<<ScreenshotEvent>>',
                              self.openScreenshot)  # 绑定截图事件
                cbox = Widget.comboboxFrame(fQuick, '截图模块：', 'scsMode')
                cbox.pack(side='top', fill='x', padx=4)
                self.balloon.bind(
                    cbox, '切换截图工作模块\n\n【Umi-OCR 软件截图】方便、精准\n【Windows 系统截图】兼容性更好')
                frss = tk.Frame(fQuick)
                frss.pack(side='top', fill='x')
                fhkUmi = tk.Frame(frss)
                fhkUmi.pack(side='top', fill='x')
                fhkU0 = tk.Frame(fhkUmi)
                fhkU0.pack(side='top', fill='x', pady=2)
                tk.Label(fhkU0, text='指示器颜色：').pack(side='left')
                self.balloon.bind(fhkU0, '修改截图时指示器的颜色\n该项目修改后，下次打开软件生效')

                def changeColor(configName, title=None):
                    initColor = Config.get(configName)
                    color = tk.colorchooser.askcolor(
                        color=initColor, title=title)
                    if color[1]:
                        Config.set(configName, color[1])
                lab1 = tk.Label(fhkU0, text='十字线', cursor='hand2', fg='blue')
                lab1.pack(side='left', padx=9)
                lab1.bind(
                    '<Button-1>', lambda *e: changeColor('scsColorLine', '截图十字线颜色'))
                lab2 = tk.Label(fhkU0, text='虚线框表层', cursor='hand2', fg='blue')
                lab2.pack(side='left', padx=9)
                lab2.bind(
                    '<Button-1>', lambda *e: changeColor('scsColorBoxUp', '截图矩形框 虚线表层颜色'))
                lab3 = tk.Label(fhkU0, text='虚线框底层', cursor='hand2', fg='blue')
                lab3.pack(side='left', padx=9)
                lab3.bind(
                    '<Button-1>', lambda *e: changeColor('scsColorBoxDown', '截图矩形框 虚线底层颜色'))
                wid = Widget.hotkeyFrame(fhkUmi, '截图识别 ', 'Screenshot',
                                         lambda *e: self.win.event_generate(
                                             '<<ScreenshotEvent>>'), isAutoBind=False)
                wid.pack(side='top', fill='x')
                self.balloon.bind(
                    wid, '关闭快捷键后，仍能通过面板上的按钮或托盘小图标调用截图\n点击【修改】可设置自定义快捷键')

                syssscom = 'win+shift+s'
                fhkSys = Widget.hotkeyFrame(frss, '系统截图 ', 'Screenshot',
                                            lambda *e: self.win.event_generate(
                                                '<<ScreenshotEvent>>'), True, syssscom, isAutoBind=False)
                self.balloon.bind(
                    fhkSys, '监听到系统截图后调用OCR\n\n若截图后软件没有反应，请确保windows系统自带的\n【截图和草图】中【自动复制到剪贴板】开关处于打开状态')

                wid = Widget.hotkeyFrame(
                    fQuick, '粘贴图片 ', 'Clipboard', self.runClipboard, isAutoBind=True)
                wid.pack(side='top', fill='x', padx=4)
                self.balloon.bind(wid, '尝试读取剪贴板，若存在图片则调用OCR\n点击【修改】可设置自定义快捷键')
                if Config.get('isAdvanced'):  # 隐藏高级选项：组合键判定调节
                    fr1 = tk.Frame(fQuick)
                    fr1.pack(side='top', fill='x', pady=2, padx=5)
                    tk.Label(fr1, text='　 组合键：').pack(side='left')
                    fr11 = tk.Frame(fr1)
                    fr11.pack(side='left')
                    self.balloon.bind(
                        fr11, '宽松：当前按下的按键只要包含设定的组合键，就能触发\n严格：当前按下的按键必须与设定的组合一致，才能触发')
                    tk.Label(fr11, text='触发判定').pack(side='left')
                    ttk.Radiobutton(fr11, text='宽松',
                                    variable=Config.getTK('isHotkeyStrict'), value=False).pack(side='left')
                    ttk.Radiobutton(fr11, text='严格',
                                    variable=Config.getTK('isHotkeyStrict'), value=True).pack(side='left')
                    fr12 = tk.Frame(fr1)
                    fr12.pack(side='left')
                    self.balloon.bind(fr12, '必须在该时间之内\n连续按下组合中的所有按键，才能触发')
                    tk.Label(fr12, text='，时限').pack(side='left')
                    tk.Entry(fr12,
                             textvariable=Config.getTK('hotkeyMaxTtl'), width=4).pack(side='left')
                    tk.Label(fr12, text='秒').pack(side='left')

                fr2 = tk.Frame(fQuick)
                fr2.pack(side='top', fill='x', pady=2, padx=5)
                fr2.grid_columnconfigure(1, minsize=20)
                wid = ttk.Checkbutton(fr2, variable=Config.getTK('isScreenshotHideWindow'),
                                      text='截图隐藏窗口')
                wid.grid(column=0, row=0)
                self.balloon.bind(
                    wid, f'截图前隐藏主窗口\n会延迟{Config.get("screenshotHideWindowWaitTime")}毫秒以等待窗口动画')
                wid = ttk.Checkbutton(fr2, variable=Config.getTK('isNeedCopy'),
                                      text='自动复制结果')
                wid.grid(column=0, row=1)
                self.balloon.bind(wid, '快捷识图完成后，将得到的文本复制到剪贴板')
                wid = ttk.Checkbutton(fr2, variable=Config.getTK('isNeedClear'),
                                      text='自动清空面板')
                wid.grid(column=2, row=1)
                self.balloon.bind(wid, f'每次快捷识图将清空识别内容面板，同时省略时间等信息')

                # 切换截图模式
                def onModeChange():
                    isHotkey = Config.get('isHotkeyScreenshot')
                    scsName = Config.get('scsModeName')
                    umihk = Config.get('hotkeyScreenshot')
                    scsMode = Config.get('scsMode').get(
                        scsName, ScsModeFlag.multi)  # 当前截屏模式
                    if scsMode == ScsModeFlag.system:  # 切换到系统截图
                        fhkUmi.forget()
                        fhkSys.pack(side='top', fill='x', padx=4)
                        self.updateFrameHeight()  # 刷新框架
                        if isHotkey:  # 当前已在注册
                            if umihk:  # 注销软件截图
                                Widget.delHotkey(umihk)  # 注销按键
                            Hotkey.add(syssscom,  # 添加快捷键监听
                                       lambda *e: self.win.event_generate('<<ScreenshotEvent>>'))
                    elif scsMode == ScsModeFlag.multi:  # 切换到软件截图
                        fhkSys.forget()
                        fhkUmi.pack(side='top', fill='x', padx=4)
                        self.updateFrameHeight()  # 刷新框架
                        if isHotkey:
                            Widget.delHotkey(syssscom)  # 注销按键
                            if umihk:
                                Hotkey.add(umihk,  # 添加快捷键监听
                                           lambda *e: self.win.event_generate('<<ScreenshotEvent>>'))
                    Log.info(f'截图模式改变：{scsMode}')
                Config.addTrace('scsModeName', onModeChange)
                onModeChange()
            quickOCR()

            # 批量任务设置
            frameBatch = tk.LabelFrame(self.optFrame, text="批量任务")
            frameBatch.pack(side='top', fill='x',
                            ipady=2, pady=LabelFramePadY, padx=4)

            def initScheduler():  # 计划任务设置
                frameScheduler = tk.LabelFrame(
                    frameBatch, labelanchor='n', text="计划任务")
                frameScheduler.pack(side='top', fill='x',
                                    ipady=2, pady=LabelFramePadY, padx=4)

                fr1 = tk.Frame(frameScheduler)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                ttk.Checkbutton(fr1, text="完成后打开文件",
                                variable=Config.getTK('isOpenOutputFile')).pack(side='left')
                ttk.Checkbutton(fr1, text="完成后打开目录",
                                variable=Config.getTK('isOpenExplorer'),).pack(side='left', padx=15)

                fr2 = tk.Frame(frameScheduler)
                fr2.pack(side='top', fill='x', pady=2, padx=5)
                ttk.Checkbutton(fr2, text='本次完成后执行',
                                variable=Config.getTK('isOkMission')).pack(side='left')
                okMissionDict = Config.get("okMission")
                okMissionNameList = [i for i in okMissionDict.keys()]
                wid = ttk.Combobox(fr2, width=14, state="readonly", textvariable=Config.getTK('okMissionName'),
                                   value=okMissionNameList)
                wid.pack(side='left')
                self.balloon.bind(wid, '可打开软件配置json文件，添加自己的任务（cmd命令）')
                if Config.get("okMissionName") not in okMissionNameList:
                    wid.current(0)  # 初始化Combobox和okMissionName
            initScheduler()

            def initInFile():  # 输入设置
                fInput = tk.LabelFrame(
                    frameBatch, labelanchor='n', text='图片导入')
                fInput.pack(side='top', fill='x',
                                 ipady=2, pady=LabelFramePadY, padx=4)
                self.balloon.bind(
                    fInput, f"允许的图片格式：\n{Config.get('imageSuffix')}")

                fr1 = tk.Frame(fInput)
                fr1.pack(side='top', fill='x', pady=2, padx=5)
                wid = ttk.Checkbutton(
                    fr1, variable=Config.getTK('isRecursiveSearch'), text='递归读取子文件夹中所有图片')
                wid.grid(column=0, row=0, columnspan=2, sticky='w')
                self.lockWidget.append(wid)
                if Config.get('isAdvanced'):  # 隐藏高级选项：修改图片许可后缀
                    tk.Label(fr1, text='图片后缀：　').grid(
                        column=0, row=2, sticky='w')
                    enInSuffix = tk.Entry(
                        fr1, textvariable=Config.getTK('imageSuffix'))
                    enInSuffix.grid(column=1, row=2, sticky='nsew')
                    self.lockWidget.append(enInSuffix)

                fr1.grid_columnconfigure(1, weight=1)
            initInFile()

            def initOutFile():  # 输出设置
                fOutput = tk.LabelFrame(
                    frameBatch, labelanchor='n', text="结果输出")
                fOutput.pack(side='top', fill='x',
                                  ipady=2, pady=LabelFramePadY, padx=4)
                # 输出文件类型勾选
                fr1 = tk.Frame(fOutput)
                fr1.pack(side='top', fill='x', pady=2, padx=5)

                wid = ttk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputTxt'), text='合并.txt文件')
                self.balloon.bind(wid, f'所有识别文本输出到同一个txt文件')
                wid.grid(column=0, row=0,  sticky='w')
                self.lockWidget.append(wid)
                wid = ttk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputSeparateTxt'), text='独立.txt文件')
                self.balloon.bind(wid, f'每张图片的文本输出到同名的单独txt文件')
                wid.grid(column=2, row=0,  sticky='w')
                self.lockWidget.append(wid)
                wid = ttk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputMD'), text='图文链接.md文件')
                self.balloon.bind(wid, f'使用Markdown阅读器打开，可同时展示图片和文本')
                wid.grid(column=0, row=1,  sticky='w')
                self.lockWidget.append(wid)
                wid = ttk.Checkbutton(
                    fr1, variable=Config.getTK('isOutputJsonl'), text='原始信息.jsonl文件')
                self.balloon.bind(wid, f'含所有文件路径和OCR信息，可导入别的程序进一步操作')
                wid.grid(column=2, row=1,  sticky='w')
                self.lockWidget.append(wid)
                tk.Label(fr1, text=' ').grid(column=1, row=0)

                def offAllOutput(e):  # 关闭全部输出
                    if OCRe.msnFlag == MsnFlag.none:
                        Config.set('isOutputTxt', False)
                        Config.set('isOutputSeparateTxt', False)
                        Config.set('isOutputMD', False)
                        Config.set('isOutputJsonl', False)
                labelOff = tk.Label(fr1, text='　 关闭全部输出',
                                    cursor='hand2', fg='blue')
                labelOff.grid(column=0, row=2, sticky='w')
                labelOff.bind('<Button-1>', offAllOutput)  # 绑定关闭全部输出

                wid = ttk.Checkbutton(fr1, text='图片中不含文字时，不输出信息',
                                      variable=Config.getTK('isIgnoreNoText'),)
                wid.grid(column=0, row=10, columnspan=9, sticky='w')
                self.lockWidget.append(wid)

                tk.Label(fOutput, fg='gray',
                         text="下面两项为空时，默认输出到第一张图片所在的文件夹"
                         ).pack(side='top', fill='x', padx=5)
                # 输出目录
                fr2 = tk.Frame(fOutput)
                fr2.pack(side='top', fill='x', pady=2, padx=5)
                tk.Label(fr2, text="输出目录：").grid(column=0, row=3, sticky='w')
                enOutPath = tk.Entry(
                    fr2, textvariable=Config.getTK('outputFilePath'))
                enOutPath.grid(column=1, row=3,  sticky='ew')
                self.lockWidget.append(enOutPath)
                fr2.grid_rowconfigure(4, minsize=2)  # 第二行拉开间距
                tk.Label(fr2, text="输出文件名：").grid(column=0, row=5, sticky='w')
                enOutName = tk.Entry(
                    fr2, textvariable=Config.getTK('outputFileName'))
                enOutName.grid(column=1, row=5, sticky='ew')
                self.lockWidget.append(enOutName)
                fr2.grid_columnconfigure(1, weight=1)  # 第二列自动扩充
            initOutFile()

            # 后处理设置
            def initProcess():  # 后处理设置
                fProcess = tk.LabelFrame(self.optFrame,  text='文本后处理')
                fProcess.pack(side='top', fill='x',
                              ipady=2, pady=LabelFramePadY, padx=4)

                fIgnore = tk.Frame(fProcess)
                fIgnore.pack(side='top', fill='x', pady=2, padx=4)

                self.ignoreBtn = ttk.Button(fIgnore, text='打开忽略区域编辑器（设置排除水印）',
                                            command=self.openSelectArea)
                self.ignoreBtn.pack(side='top', fill='x')
                self.balloon.bind(
                    self.ignoreBtn, '忽略图片中的指定区域\n可用于批量识别时排除图片水印')
                self.lockWidget.append(self.ignoreBtn)
                # 忽略区域本体框架
                self.ignoreFrame = tk.Frame(fIgnore)  # 不pack，动态添加
                self.ignoreFrame.grid_columnconfigure(0, minsize=4)
                wid = ttk.Button(self.ignoreFrame, text='添加区域',
                                 command=self.openSelectArea)
                wid.grid(column=1, row=0, sticky='w')
                self.lockWidget.append(wid)
                wid = ttk.Button(self.ignoreFrame, text='清空区域',
                                 command=self.clearArea)
                wid.grid(column=1, row=1, sticky='w')
                self.lockWidget.append(wid)
                self.ignoreLabel = tk.Label(
                    self.ignoreFrame, anchor='w', justify='left')  # 显示生效大小
                self.ignoreLabel.grid(column=1, row=2, sticky='n')
                self.balloon.bind(
                    self.ignoreLabel, '批量任务时，只有分辨率与之相同的图片，才会应用忽略区域。')
                self.ignoreFrame.grid_rowconfigure(2, minsize=10)
                self.ignoreFrame.grid_columnconfigure(2, minsize=4)
                self.canvasHeight = 120  # 画板高度不变，宽度根据选区回传数据调整
                self.canvas = tk.Canvas(self.ignoreFrame, width=200, height=self.canvasHeight,
                                        bg="black", cursor='hand2')
                self.canvas.grid(column=3, row=0, rowspan=10)
                self.canvas.bind(
                    '<Button-1>', lambda *e: self.openSelectArea())
                fpro = tk.Frame(fProcess)
                fpro.pack(side='top', fill='x', pady=2, padx=4)
                fpro.grid_columnconfigure(0, weight=1)
                wid = Widget.comboboxFrame(
                    fpro, '合并段落：　', 'tbpu', self.lockWidget)
                wid.grid(column=0, row=0, sticky='ew')
                self.balloon.bind(wid, '将OCR划分的单行文本合并成整段文字\n点击右侧按钮，浏览方案说明')
                labelUse = tk.Label(fpro, text='说明', width=5,
                                    fg='deeppink', cursor='question_arrow')
                labelUse.grid(column=1, row=0)
                labelUse.bind(
                    '<Button-1>', lambda *e: self.showTips(GetTbpuHelp(Umi.website)))  # 绑定鼠标左键点击
            initProcess()

            def initOcrUI():  # OCR引擎设置
                frameOCR = tk.LabelFrame(
                    self.optFrame, text="OCR识别引擎设置")
                frameOCR.pack(side='top', fill='x', ipady=2,
                              pady=LabelFramePadY, padx=4)
                wid = Widget.comboboxFrame(
                    frameOCR, '识别语言：　', 'ocrConfig', self.lockWidget)
                wid.pack(side='top', fill='x', pady=2, padx=5)
                self.balloon.bind(
                    wid, '本软件有整理好的多国语言扩展包，可导入更多语言模型库，\n也可以手动导入PaddleOCR兼容的模型库，\n详情请浏览项目Github主页\n\n竖排模型库（识别语言）建议与竖排合并段落搭配使用')
                # 压缩
                fLim = tk.Frame(frameOCR)
                fLim.pack(side='top', fill='x', pady=2, padx=5)
                self.balloon.bind(
                    fLim, '长边压缩模式可以大幅加快识别速度，但可能降低大分辨率图片的识别准确率\n大于4000像素的图片，可将数值改为最大边长的一半。必须为大于零的整数\n默认值： 960\n\n短边扩大模式可能提高小分辨率图片的准确度。一般用不着')
                Widget.comboboxFrame(
                    fLim, '缩放预处理：', 'ocrLimitMode', self.lockWidget, 14).pack(side='left')
                tk.Label(fLim, text='至').pack(side='left')
                wid = tk.Entry(
                    fLim, width=9, textvariable=Config.getTK('ocrLimitSize'))
                wid.pack(side='left')
                self.lockWidget.append(wid)
                tk.Label(fLim, text='像素').pack(side='left')
                # 方向
                wid = ttk.Checkbutton(frameOCR, text='启用方向分类器（文字偏转90度/180度方向矫正）',
                                      variable=Config.getTK('isOcrAngle'))
                wid.pack(side='top', fill='x', pady=2, padx=5)
                self.balloon.bind(
                    wid, '当图片中的文字偏转90度或180度时，请打开该选项\n可能略微降低识别速度\n小角度偏转无需启用该选项')
                self.lockWidget.append(wid)
                # CPU
                fCpu = tk.Frame(frameOCR, padx=5)
                fCpu.pack(side='top', fill='x')
                tk.Label(fCpu, text='线程数：').pack(side='left')
                wid = tk.Entry(
                    fCpu, width=6, textvariable=Config.getTK('ocrCpuThreads'))
                wid.pack(side='left')
                self.lockWidget.append(wid)
                self.balloon.bind(
                    wid, '最好等于CPU的线程数目。必须为大于零的整数')
                wid = ttk.Checkbutton(fCpu, text='启用MKLDNN加速',
                                      variable=Config.getTK('isOcrMkldnn'))
                wid.pack(side='left', padx=40)
                self.balloon.bind(
                    wid, '大幅加快识别速度。内存占用也会增加')
                self.lockWidget.append(wid)

                # grid
                fr1 = tk.Frame(frameOCR)
                fr1.pack(side='top', fill='x', padx=5)
                if Config.get('isAdvanced'):
                    # 隐藏高级选项：额外启动参数
                    tk.Label(fr1, text='额外启动参数：').grid(
                        column=0, row=2, sticky='w')
                    wid = tk.Entry(
                        fr1, textvariable=Config.getTK('argsStr'))
                    wid.grid(column=1, row=2, sticky="nsew")
                    self.balloon.bind(
                        wid, 'OCR高级参数指令。请遵守PaddleOCR-json要求的格式。详情参考项目主页')
                    self.lockWidget.append(wid)
                    # 隐藏高级选项：引擎管理策略
                    Widget.comboboxFrame(fr1, '引擎管理策略：', 'ocrRunMode', self.lockWidget
                                         ).grid(column=0, row=6, columnspan=2, sticky='we')

                frState = tk.Frame(fr1)
                frState.grid(column=0, row=7, columnspan=2, sticky='nsew')
                tk.Label(frState, text='引擎当前状态：').pack(
                    side='left')
                tk.Label(frState, textvariable=Config.getTK('ocrProcessStatus')).pack(
                    side='left')
                labStop = tk.Label(frState, text="停止",
                                   cursor='hand2', fg="red")
                labStop.pack(side='right')
                self.balloon.bind(labStop, '强制停止引擎进程')
                labStart = tk.Label(frState, text="启动",
                                    cursor='hand2', fg='blue')
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
                    self.optFrame, text='关于')
                frameAbout.pack(side='top', fill='x', ipady=2,
                                pady=LabelFramePadY, padx=4)
                tk.Label(frameAbout, image=Asset.getImgTK(
                    'umiocr64')).pack()  # 图标
                tk.Label(frameAbout, text=Umi.name, fg='gray').pack()
                tk.Label(frameAbout, text=Umi.about, fg='gray').pack()
                labelWeb = tk.Label(frameAbout, text=Umi.website, cursor='hand2',
                                    fg='deeppink')
                labelWeb.pack()  # 文字
                labelWeb.bind(  # 绑定鼠标左键点击，打开网页
                    '<Button-1>', lambda *e: webOpen(Umi.website))
            initAbout()

            def initEX():  # 额外
                fEX = tk.Frame(self.optFrame)
                fEX.pack(side='top', fill='x', padx=4)
                labelOpenFile = tk.Label(
                    fEX, text='打开设置文件', fg='gray', cursor='hand2')
                labelOpenFile.pack(side='left')
                labelOpenFile.bind(
                    '<Button-1>', lambda *e: os.startfile('Umi-OCR_config.json'))
                self.balloon.bind(labelOpenFile, 'Umi-OCR_config.json')
                wid = tk.Checkbutton(fEX, text='调试模式', fg='gray',
                                     variable=Config.getTK('isDebug'))
                self.balloon.bind(
                    wid, '调试功能，供开发者使用，立即生效：\nOCR输出额外调试信息 | 内置截图显示调试器')
                wid.pack(side='right')
                # 隐藏高级选项
                wid = tk.Checkbutton(fEX, text='高级选项', fg='gray',
                                     variable=Config.getTK('isAdvanced'))
                self.balloon.bind(
                    wid, '启用隐藏的高级选项，重启后生效：\n组合键判定规则 | 图片许可后缀 | 引擎启动参数 | 引擎管理策略')
                wid.pack(side='right', padx=10)
                # 若初始时非置顶，不显示提示，则尾部预留出空间
                if not Config.get('isWindowTop'):
                    tk.Label(self.optFrame).pack(side='top')
            initEX()

            def initOptFrameWH():  # 初始化框架的宽高
                self.updateFrameHeight()
                self.optCanvasWidth = 1  # 宽度则是随窗口大小而改变。

                def onCanvasResize(event):  # 绑定画布大小改变事件
                    cW = event.width-3  # 当前 画布宽度
                    if not cW == self.optCanvasWidth:  # 若与上次不同：
                        self.optFrame['width'] = cW  # 修改设置页 框架宽度
                        self.optCanvasWidth = cW
                self.optCanvas.bind(  # 绑定画布大小改变事件。只有画布组件前台显示时才会触发，减少性能占用
                    '<Configure>', onCanvasResize)

                def onCanvasMouseWheel(event):  # 绑定画布中滚轮滚动事件
                    self.optCanvas.yview_scroll(
                        1 if event.delta < 0 else -1, "units")
                self.optCanvas.bind_all('<MouseWheel>', onCanvasMouseWheel)
                # 为所有复选框解绑默认滚轮事件，防止误触
                self.win.unbind_class('TCombobox', '<MouseWheel>')
            initOptFrameWH()
        initTab3()

        # 解析启动参数
        def getArgs():
            try:
                parser = ArgumentParser()
                parser.add_argument('--no_win', dest='isNoWin', type=bool)
                return parser.parse_args()
            except Exception as e:
                tk.messagebox.showerror(
                    '遇到了一点小问题', f'程序启动参数解析失败。已切换为默认参数。\n{e}')

                class aaa:
                    isNoWin = False
                return aaa()
        args = getArgs()

        if Config.get('isTray'):  # 启动托盘
            SysTray.start()
            self.win.wm_protocol(  # 注册窗口关闭事件
                'WM_DELETE_WINDOW', self.onCloseWin)
            if not args.isNoWin:  # 非静默模式
                self.gotoTop()  # 恢复主窗显示
        else:  # 无托盘，强制显示主窗
            self.gotoTop()
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
        suf = Config.get('imageSuffix')  # 许可后缀
        paths = tk.filedialog.askopenfilenames(
            title='选择图片', filetypes=[('图片', suf)])
        self.addImagesList(paths)

    def addImagesList(self, paths):  # 添加一批图片列表
        suf = Config.get('imageSuffix').split()  # 许可后缀列表

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
        if not OCRe.msnFlag == MsnFlag.none or not self.win.attributes('-disabled') == 0:
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
            self.ignoreFrame.pack_forget()  # 隐藏忽略区域窗口
            self.ignoreBtn.pack(side='top', fill='x')  # 显示按钮
            self.updateFrameHeight()  # 刷新框架
            return
        self.ignoreLabel["text"] = f"生效分辨率：\n宽 {area['size'][0]}\n高 {area['size'][1]}"
        self.canvas.delete(tk.ALL)  # 清除画布
        scale = self.canvasHeight / area['size'][1]  # 显示缩放比例
        width = round(self.canvasHeight * (area['size'][0] / area['size'][1]))
        self.canvas['width'] = width
        areaColor = ["red", "green", "darkorange"]
        tran = 2  # 绘制偏移量
        for i in range(3):  # 绘制新图
            for a in area['area'][i]:
                x0, y0 = a[0][0]*scale+tran, a[0][1]*scale+tran,
                x1, y1 = a[1][0]*scale+tran, a[1][1]*scale+tran,
                self.canvas.create_rectangle(
                    x0, y0, x1, y1,  fill=areaColor[i])
        self.ignoreBtn.pack_forget()  # 隐藏按钮
        self.ignoreFrame.pack(side='top', fill='x')  # 显示忽略区域窗口
        self.updateFrameHeight()  # 刷新框架

    def clearArea(self):  # 清空忽略区域
        self.ignoreFrame.pack_forget()  # 隐藏忽略区域窗口
        self.ignoreBtn.pack(side='top', fill='x')  # 显示按钮
        self.updateFrameHeight()  # 刷新框架
        Config.set("ignoreArea", None)
        self.canvas.delete(tk.ALL)  # 清除画布
        self.canvas['width'] = int(self.canvasHeight * (16/9))

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

    def panelOutput(self, text, position=tk.END, highlight=''):
        '''输出面板写入文字'''
        self.textOutput.insert(position, text)
        if highlight:  # 需要高亮
            if position == tk.END:  # 暂时只允许尾部插入
                self.textOutput.tag_add(  # 尾部插入要高亮前一行
                    highlight, f'end -1lines linestart', f'end -1lines lineend')
        if self.isAutoRoll.get():  # 需要自动滚动
            self.textOutput.see(position)

    def panelClear(self):
        '''清空输出面板'''
        self.textOutput.delete('1.0', tk.END)

    # 窗口操作 =============================================

    def updateFrameHeight(self):  # 刷新设置页框架高度
        self.optFrame.pack_propagate(True)  # 启用框架自动宽高调整
        self.optFrame.update()  # 强制刷新
        rH = self.optFrame.winfo_height()  # 由组件撑起的 框架高度
        self.optCanvas.config(scrollregion=(0, 0, 0, rH))  # 画布内高度为框架高度
        self.optFrame.pack_propagate(False)  # 禁用框架自动宽高调整
        self.optFrame["height"] = rH  # 手动还原高度

    def gotoTop(self, isForce=False):  # 主窗置顶
        flag = Config.get('WindowTopMode')
        if flag == WindowTopModeFlag.never and not isForce:  # 模式：从不置顶
            self.win.attributes('-topmost', 0)
            return
        if self.win.state() == 'iconic':  # 窗口最小化状态下
            self.win.state('normal')  # 恢复前台状态
        self.win.attributes('-topmost', 1)  # 设置层级最前
        geometry = self.win.geometry()  # 缓存主窗当前位置大小
        self.win.deiconify()  # 主窗获取焦点
        self.win.geometry(geometry)  # 若主窗正在贴边，获取焦点会退出贴边模式，所以重新设置位置恢复贴边
        if flag == WindowTopModeFlag.eternity:  # 模式：窗口永远置顶
            return
        # 模式：自动弹出，一段时间后解除置顶
        self.win.after(500, lambda: self.win.attributes('-topmost', 0))

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
            Config.set('tipsTop1', '')
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
                elif 'state' in w.keys():
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

    def startSingleClipboard(self):  # 开始单张识别的剪贴板任务
        try:  # 初始化快捷识图任务处理器
            msnQui = MsnQuick()
        except Exception as err:
            tk.messagebox.showwarning('遇到了亿点小问题', f'{err}')
            return  # 未开始运行，终止本次运行
        # 开始运行
        OCRe.runMission(['clipboard'], msnQui)
        self.notebook.select(self.notebookTab[1])  # 转到输出卡
        self.gotoTop()  # 主窗置顶

    def runClipboard(self, e=None):  # 识别剪贴板
        if not OCRe.msnFlag == MsnFlag.none:  # 正在运行，不执行
            return
        clipData = Tool.getClipboardFormat()  # 读取剪贴板

        failFlag = False

        # 剪贴板中是位图（优先）
        if isinstance(clipData, int):
            self.startSingleClipboard()

        # 剪贴板中是文件列表（文件管理器中对着文件ctrl+c得到句柄）
        elif isinstance(clipData, tuple):
            # 检验文件列表中是否存在合法文件类型
            suf = Config.get('imageSuffix').split()  # 许可后缀列表
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
                failFlag = True
        else:  # 剪贴板中不是支持的格式
            failFlag = True

        if failFlag:
            self.panelOutput('剪贴板中未查询到图片信息\n')
            # 失败也置顶
            self.gotoTop()  # 主窗置顶
            self.notebook.select(self.notebookTab[1])  # 转到输出卡

    def openScreenshot(self, e=None):  # 打开截图窗口
        if not OCRe.msnFlag == MsnFlag.none or not self.win.attributes('-disabled') == 0:
            return
        self.win.attributes("-disabled", 1)  # 禁用主窗口
        if Config.get('isScreenshotHideWindow'):  # 截图时隐藏主窗口
            self.win.state('iconic')
            self.win.after(Config.get('screenshotHideWindowWaitTime'),
                           ScreenshotCopy)  # 延迟，等待最小化完成再截屏
        else:
            ScreenshotCopy()  # 立即截屏

    def closeScreenshot(self, flag, errMsg=None):  # 关闭截图窗口，返回T表示已复制到剪贴板
        self.win.attributes("-disabled", 0)  # 启用父窗口
        if errMsg:
            self.panelOutput(f'截图失败，{errMsg}')
        if not flag and self.win.state() == 'normal':  # 截图不成功，但窗口非最小化
            self.gotoTop()  # 主窗置顶
        elif flag:  # 成功
            # self.win.after(50, self.runClipboard)
            self.startSingleClipboard()  # 剪贴板识图

    def onCloseWin(self):  # 关闭窗口事件
        if Config.get('isBackground'):
            self.win.withdraw()  # 隐藏窗口
        else:
            self.onClose()  # 直接关闭

    def onClose(self):  # 关闭软件
        OCRe.stop()  # 强制关闭引擎进程，加快子线程结束
        if OCRe.engFlag == EngFlag.none and OCRe.msnFlag == MsnFlag.none:  # 未在运行
            self.exit()
        else:
            self.win.after(50, self.waitClose)  # 等待关闭，50ms轮询一次是否已结束子线程

    def waitClose(self):  # 等待线程关闭后销毁窗口
        Log.info(f'关闭中，等待 {OCRe.engFlag} | {OCRe.msnFlag}')
        if OCRe.engFlag == EngFlag.none and OCRe.msnFlag == MsnFlag.none:  # 未在运行
            self.exit()
        else:
            self.win.after(50, self.waitClose)  # 等待关闭，50ms轮询一次是否已结束子进程

    def exit(self):
        SysTray.stop()  # 关闭托盘。这个函数里有判断，不会造成无限递归。
        # 等待一段时间，保证托盘线程关闭，图标从系统注销
        # 然后强制终止主进程，防止引擎子线程苟且偷生
        self.win.after(100, lambda: os._exit(0))

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
            self.panelClear()
        self.textOutput.insert(tk.END, tipsText)

# 全角空格：【　】
