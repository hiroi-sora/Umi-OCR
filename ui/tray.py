from ui.systray.traybar import SysTrayIcon
from utils.asset import Asset
from utils.config import Config


class Tray:

    def __init__(self):
        menuOptions = (
            ('屏幕截图', Asset.getPath('screenshot24ico'), self.screenshot),
            ('粘贴图片', Asset.getPath('paste24ico'), self.clipboard),
            ("显示界面", Asset.getPath('app24ico'), self.showWin),
        )
        self.tray = SysTrayIcon(
            Asset.getPath('umiocr24ico'),
            'Umi-OCR', menuOptions,
            quit_name='退出',
            quit_icon=Asset.getPath('exit24ico'),
            on_quit=self.quit)

    def start(self):
        self.tray.start()
        self.main = Config.main
        # 注册事件，防止跨线程调用方法
        self.main.win.bind(
            '<<QuitEvent>>', lambda *e: self.main.onClose())
        self.main.win.bind(
            '<<ClipboardEvent>>', lambda *e: self.main.runClipboard())
        # <<ScreenshotEvent>> 在主窗类内已注册

    def stop(self):
        '''关闭托盘显示的接口。必须在主线程调用，禁止在托盘线程内调用！'''
        # https://github.com/Infinidat/infi.systray/issues/26
        # https://github.com/Infinidat/infi.systray/issues/32
        self.tray.shutdown()

    def showWin(self, e=None):
        self.main.gotoTop()

    def screenshot(self, e=None):
        self.main.win.event_generate('<<ScreenshotEvent>>')

    def clipboard(self, e=None):
        self.main.win.event_generate('<<ClipboardEvent>>')

    def quit(self, e=None):
        self.main.win.event_generate('<<QuitEvent>>')


SysTray = Tray()  # 托盘单例
