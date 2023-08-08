# ========================================================
# =============== 键盘/鼠标连接器，在qml调用 ===============
# ========================================================

from PySide2.QtCore import QObject, Slot

from .keyboard import HotkeyCtrl


class KeyMouseConnector(QObject):
    # ========================= 【热键】 =========================

    # 注册热键
    @Slot(str, str, int, result=str)
    def addHotkey(self, keysName, title, press):
        return HotkeyCtrl.addHotkey(keysName, title, press)

    # 取消热键
    @Slot(str, str, int)
    def delHotkey(self, keysName, title, press):
        return HotkeyCtrl.delHotkey(keysName, title, press)

    # 开始录制热键
    @Slot(str, str, result=str)
    def readHotkey(self, runningTitle, finishTitle):
        return HotkeyCtrl.readHotkey(runningTitle, finishTitle)
