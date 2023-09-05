# 快捷方式生成/删除
# 开机自启，开始菜单，桌面快捷方式

from PySide2.QtCore import QStandardPaths as Qsp, QFile, QFileInfo, QFileDevice
import os

from ..platform import Platform


class _ShortcutApi:
    @staticmethod  # 获取地址
    def __getPath(position):
        if position == "desktop":
            return Qsp.writableLocation(Qsp.DesktopLocation)
        elif position == "startMenu":
            return Platform.StandardPaths.GetStartMenu()
        elif position == "startup":
            return Platform.StandardPaths.GetStartup()

    @staticmethod  # 创建快捷方式
    def createShortcut(position):
        lnkName = os.environ["APP_NAME"] + ".lnk"
        appPath = os.environ["APP_PATH"]
        lnkPath = _ShortcutApi.__getPath(position)
        lnkPath = os.path.join(lnkPath, lnkName)
        try:
            fApp = QFile(appPath)
            fApp.link(lnkPath)
        except QFileDevice.PermissionError as e:
            return f"[Error] Insufficient permissions, creating shortcut failed.\n【异常】权限不足，无法创建快捷方式。请以管理员权限打开软件进行操作。\n{e}"
        except Exception as e:
            return f"[Error] Failed to create shortcut.\n【异常】创建快捷方式失败。\n{e}"

    @staticmethod  # 删除快捷方式
    def deleteShortcut(position):
        appName = os.environ["APP_NAME"]
        lnkDir = _ShortcutApi.__getPath(position)
        num = 0
        for fileName in os.listdir(lnkDir):
            lnkPath = os.path.join(lnkDir, fileName)
            try:
                if not os.path.isfile(lnkPath):  # 排除非文件
                    continue
                info = QFileInfo(lnkPath)
                if not info.isSymLink():  # 排除非快捷方式
                    continue
                originName = os.path.basename(info.symLinkTarget())
                if appName in originName:  # 快捷方式指向的文件名包含appName，删之
                    os.remove(lnkPath)
                    num += 1
            except Exception as e:
                print(f"[Error] 删除快捷方式失败 {lnkPath}: {e}")
                continue
        return num


print("== 创建快捷", _ShortcutApi.createShortcut("desktop"))
print("== 删除快捷", _ShortcutApi.deleteShortcut("desktop"))
