# ==============================================
# =============== Linux系统API ===============
# ==============================================

import os
import shlex
import subprocess
from .key_translator import getKeyName


# ==================== 标准路径 ====================
# TODO: 获取系统的标准路径
class _StandardPaths:
    @staticmethod
    def GetStartMenu():
        """获取开始菜单路径"""
        return "TODO: 获取开始菜单路径"

    @staticmethod
    def GetStartup():
        """获取启动（开机自启）路径"""
        return "TODO: 获取开机自启路径"


# ==================== 硬件控制 ====================
class _HardwareCtrl:
    # 关机
    @staticmethod
    def shutdown():
        # TODO: sudo权限？
        os.system("sudo shutdown -h now")

    # 休眠
    @staticmethod
    def hibernate():
        os.system("sudo systemctl hibernate")


# ==================== 对外接口 ====================
class Api:
    # 系统标准路径。接口： GetStartMenu GetStartup
    StandardPaths = _StandardPaths()

    # 硬件控制。接口： shutdown hibernate
    HardwareCtrl = _HardwareCtrl()

    # TODO: 根据系统及硬件，判断最适合的渲染器类型
    @staticmethod
    def getOpenGLUse():
        return "AA_UseOpenGLES"  # 默认使用GLES。
        # return "AA_UseSoftwareOpenGL" # 如果不兼容？则使用软渲染

    # 键值转键名
    @staticmethod
    def getKeyName(key):
        return getKeyName(key)

    # 让系统运行一个程序，不堵塞当前进程
    @staticmethod
    def runNewProcess(path, args=""):
        # TODO: 测试、完善
        command_line = [path] + shlex.split(args)
        subprocess.Popen(command_line)

    # 用系统默认应用打开一个文件或目录，不堵塞当前进程
    @staticmethod
    def startfile(path):
        os.startfile(path)
