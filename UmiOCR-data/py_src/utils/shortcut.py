# 快捷方式生成/删除
# 开机自启，开始菜单，桌面快捷方式

from PySide2.QtCore import QStandardPaths as Qsp, QFile, QFileInfo, QFileDevice
import os

from umi_about import UmiAbout  # 项目信息
from ..platform import Platform


class ShortcutApi:
    @staticmethod  # 获取地址
    def _getPath(position):
        if position == "desktop":
            return Qsp.writableLocation(Qsp.DesktopLocation)
        elif position == "startMenu":
            return Platform.StandardPaths.GetStartMenu()
        elif position == "startup":
            return Platform.StandardPaths.GetStartup()

    @staticmethod  # 创建快捷方式，返回成功与否的字符串
    def createShortcut(position):
        lnkName = "Umi-OCR"
        appPath = UmiAbout["app"]["path"]
        if not appPath:
            return "未找到 Umi-OCR.exe 。请尝试手动创建快捷方式。\n[Error] Umi-OCR app path not exist. Please try creating a shortcut manually."
        lnkPathBase = ShortcutApi._getPath(position)
        lnkPathBase = os.path.join(lnkPathBase, lnkName)
        lnkPath = lnkPathBase + ".lnk"
        i = 1
        while os.path.exists(lnkPath):  # 快捷方式已存在
            lnkPath = lnkPathBase + f" ({i}).lnk"  # 添加序号
            i += 1
        appFile = QFile(appPath)
        res = appFile.link(lnkPath)
        if not res:
            return f"[Error] {appFile.errorString()}\n请尝试以管理员权限启动软件。\nPlease try starting the software as an administrator.\nappPath: {appPath}\nlnkPath: {lnkPath}"
        return "[Success]"

    @staticmethod  # 删除快捷方式
    def deleteShortcut(position):
        appName = "Umi-OCR"
        lnkDir = ShortcutApi._getPath(position)
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
