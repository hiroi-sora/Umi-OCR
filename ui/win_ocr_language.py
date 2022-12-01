# 更改OCR语言
from ui.widget import Widget  # 控件
from utils.config import Config
from utils.asset import Asset  # 资源
from utils.data_structure import KeyList
from utils.hotkey import Hotkey
from utils.logger import GetLog

import tkinter as tk
from tkinter import ttk

Log = GetLog()


class OcrLanguageWin:
    def __init__(self):
        self.lanList = KeyList()
        self.win = None

    def _initWin(self):
        # 主窗口
        self.win = tk.Toplevel()
        self.win.iconphoto(False, Asset.getImgTK('umiocr24'))  # 设置窗口图标
        self.win.minsize(250, 340)  # 最小大小
        self.win.geometry(f"{250}x{340}")
        self.win.unbind('<MouseWheel>')
        self.win.title('更改语言')
        self.win.wm_protocol(  # 注册窗口关闭事件
            'WM_DELETE_WINDOW', self.exit)
        fmain = tk.Frame(self.win, padx=4, pady=4)
        fmain.pack(fill='both', expand=True)

        # 顶部信息
        ftop = tk.Frame(fmain)
        ftop.pack(side='top', fill='x')
        tk.Label(ftop, text='当前：').pack(side='left')
        tk.Label(ftop, textvariable=Config.getTK(
            'ocrConfigName')).pack(side='left')
        wid = tk.Label(ftop, text='提示', fg='deeppink', cursor='question_arrow')
        wid.pack(side='right')
        Config.main.balloon.bind(
            wid, '''窗口操作：
1. 正常时，切换语言立即生效
2. 若在任务进行中切换语言，将在下次任务时生效
3. 主窗口启用/取消置顶后，需重新打开本窗口，才能使本窗口设为相应的置顶状态

更多语言：
本软件有整理好的多国语言扩展包，可导入更多语言模型库。也可以
手动导入PaddleOCR兼容的模型库，详情请浏览项目Github主页。''')

        # 中部控制
        fmiddle = tk.Frame(fmain, pady=4)
        fmiddle.pack(side='top', expand=True, fill='both')
        fmiddle.grid_columnconfigure(0, weight=1)

        # 语言表格
        ftable = tk.Frame(fmiddle, bg='red')
        ftable.pack(side='left', expand=True, fill='both')
        self.table = ttk.Treeview(
            master=ftable,  # 父容器
            # height=50,  # 表格显示的行数,height行
            columns=['ConfigName'],  # 显示的列
            show='headings',  # 隐藏首列
        )
        self.table.pack(expand=True, side='left', fill='both')
        self.table.heading('ConfigName', text='语言')
        self.table.column('ConfigName', minwidth=40)
        vbar = tk.Scrollbar(  # 绑定滚动条
            ftable, orient='vertical', command=self.table.yview)
        vbar.pack(side='left', fill='y')
        self.table["yscrollcommand"] = vbar.set
        self.table.bind('<ButtonRelease-1>',  # 绑定鼠标松开。按下时先让表格组件更新，松开才能获取到最新值
                        lambda *e: self.updateLanguage())

        # fmright = tk.Frame(fmiddle)
        # fmright.pack(side='left', fill='y')
        # tk.Label(fmright, text='右侧').pack(side='left')

        # 底部控制
        fbottom = tk.Frame(fmain)
        fbottom.pack(side='top', fill='x')
        Widget.comboboxFrame(fbottom, '合并段落：', 'tbpu').pack(
            side='top', fill='x', pady=3)
        wid = ttk.Checkbutton(fbottom, variable=Config.getTK('isLanguageWinAutoOcr'),
                              text='立即识图')
        wid.pack(side='left')
        Config.main.balloon.bind(wid, '修改语言后，立即以当前语言进行一次剪贴板识图')
        wid = ttk.Button(fbottom, text='关闭', width=5,
                         command=self.exit)
        wid.pack(side='right')
        wid = ttk.Checkbutton(fbottom, variable=Config.getTK('isLanguageWinAutoExit'),
                              text='自动关闭')
        wid.pack(side='right', padx=10)
        Config.main.balloon.bind(wid, '修改语言后，立即关闭本窗口')

        self.updateTable()

    def open(self):
        if self.win:
            self.win.state('normal')  # 恢复前台状态
        else:
            self._initWin()  # 初始化窗口
        self.win.attributes('-topmost', 1)  # 设置层级最前
        if Config.get('isWindowTop'):
            self.win.title('更改语言(置顶)')
        else:
            self.win.title('更改语言')
            self.win.attributes('-topmost', 0)  # 解除
        # 窗口移动到鼠标附近
        (x, y) = Hotkey.getMousePos()
        w = self.win.winfo_width()
        h = self.win.winfo_height()
        if w < 2:
            w = 250
        if h < 2:
            h = 340
        w1 = self.win.winfo_screenwidth()
        h1 = self.win.winfo_screenheight()
        x -= round(w/2)
        y -= 140
        # 防止窗口超出屏幕
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > w1-w:
            x = w1-w
        if y > h1-h-70:
            y = h1-h-70
        self.win.geometry(f"+{x}+{y}")

    def updateTable(self):  # 刷新语言表格
        configDist = Config.get('ocrConfig')
        configName = Config.get('ocrConfigName')
        for key, value in configDist.items():
            tableInfo = (key)
            dictInfo = {'key': key}
            id = self.table.insert('', 'end', values=tableInfo)  # 添加到表格组件中
            self.lanList.append(id, dictInfo)
            if key == configName:
                self.table.selection_set(id)

    def updateLanguage(self):  # 刷新选中语言，写入配置
        chi = self.table.selection()
        if len(chi) == 0:
            return
        chi = chi[0]
        lan = self.lanList.get(key=chi)['key']
        Config.set('ocrConfigName', lan)
        if Config.get('isLanguageWinAutoExit'):  # 自动关闭
            self.exit()
        if Config.get('isLanguageWinAutoOcr'):  # 重复任务
            Config.main.runClipboard()

    def exit(self):
        self.win.withdraw()  # 隐藏窗口


lanWin = OcrLanguageWin()


def ChangeOcrLanguage():
    lanWin.open()
