from logging import raiseExceptions
from ui.systray.traybar import SysTrayIcon
from utils.asset import Asset
from utils.config import Umi
from utils.config import Config, ClickTrayModeFlag
from ui.win_ocr_language import ChangeOcrLanguage  # 更改语言

import atexit  # 退出处理


class Tray:

    def __init__(self):
        self.tray = None

    def start(self):
        aa = ('显示面板', Asset.getPath('app24ico'), self.showWin)
        bb = ('屏幕截图', Asset.getPath('screenshot24ico'), self.screenshot)
        cc = ('粘贴图片', Asset.getPath('paste24ico'), self.clipboard)
        dd = ('更改语言', Asset.getPath('language24ico'),
              lambda *e: ChangeOcrLanguage())
        clickTrayMode = Config.get('clickTrayMode').get(
            Config.get('clickTrayModeName'), ClickTrayModeFlag.show)
        menuOptions = ()
        if clickTrayMode == ClickTrayModeFlag.show:
            menuOptions = (aa, bb, cc, dd)
        elif clickTrayMode == ClickTrayModeFlag.screenshot:
            menuOptions = (bb, cc, aa, dd)
        elif clickTrayMode == ClickTrayModeFlag.clipboard:
            menuOptions = (cc, bb, aa, dd)
        self.tray = SysTrayIcon(
            Asset.getPath('umiocrico'),
            Umi.name, menuOptions,
            quit_name='退出',
            quit_icon=Asset.getPath('exit24ico'),
            on_quit=self.quit)
        self.tray.start()
        atexit.register(self.stop)  # 注册程序终止时执行强制停止子进程
        self.main = Config.main
        # 注册事件，防止跨线程调用方法
        self.main.win.bind(
            '<<QuitEvent>>', lambda *e: self.main.onClose())
        # self.main.win.bind(
        #     '<<QuitEvent>>', lambda *e: self.main.exit())
        self.main.win.bind(
            '<<ClipboardEvent>>', lambda *e: self.main.runClipboard())
        # <<ScreenshotEvent>> 在主窗类内已注册

    def stop(self):
        '''关闭托盘显示的接口。必须在主线程调用，禁止在托盘线程内调用！'''
        # https://github.com/Infinidat/infi.systray/issues/26
        # https://github.com/Infinidat/infi.systray/issues/32
        if not self.tray:
            return
        self.tray.shutdown()
        self.tray = None  # 将引用置空，主窗口第二次按下关闭时可强行关闭

    def showWin(self, e=None):
        self.main.gotoTop(isForce=True)

    def screenshot(self, e=None):
        self.main.win.event_generate('<<ScreenshotEvent>>')

    def clipboard(self, e=None):
        self.main.win.event_generate('<<ClipboardEvent>>')

    def quit(self, e=None):
        if self.main.win:
            self.main.win.event_generate('<<QuitEvent>>')


SysTray = Tray()  # 托盘单例
