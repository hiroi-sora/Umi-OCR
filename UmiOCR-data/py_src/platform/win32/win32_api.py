# ==============================================
# =============== Windows系统API ===============
# ==============================================

import os
import subprocess
from .key_translator import getKeyName


# ==================== 标准路径 ====================
# 获取系统的标准路径
class _StandardPaths:
    # 获取开始菜单路径。传值：user 用户菜单 | common 公共菜单
    @staticmethod
    def GetStartMenu(type="common"):
        if type == "user":
            return os.getenv("APPDATA") + "\\Microsoft\\Windows\\Start Menu"
        elif type == "common":
            return os.getenv("ProgramData") + "\\Microsoft\\Windows\\Start Menu"

    # 获取启动（开机自启）路径。
    @staticmethod
    def GetStartup(type="common"):
        return _StandardPaths.GetStartMenu(type) + "\\Programs\\Startup"


# ==================== 硬件控制 ====================
class _HardwareCtrl:
    # 关机
    @staticmethod
    def shutdown():
        os.system("shutdown /s /t 0")

    # 休眠
    @staticmethod
    def hibernate():
        os.system("shutdown /h")


# ==================== 对外接口 ====================
class Api:
    # 系统标准路径。接口： GetStartMenu GetStartup
    StandardPaths = _StandardPaths()

    # 硬件控制。接口： shutdown hibernate
    HardwareCtrl = _HardwareCtrl()

    # 键值转键名
    @staticmethod
    def getKeyName(key):
        return getKeyName(key)

    # 让系统运行一个程序，不堵塞当前进程
    @staticmethod
    def runNewProcess(path):
        subprocess.Popen(f'start "" "{path}"', shell=True)

    # 用系统默认应用打开一个文件或目录，不堵塞当前进程
    @staticmethod
    def startfile(path):
        os.startfile(path)
