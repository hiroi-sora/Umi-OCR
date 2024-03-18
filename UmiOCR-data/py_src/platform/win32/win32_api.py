# ==============================================
# =============== Windows系统API ===============
# ==============================================

import os
import subprocess
from .key_translator import getKeyName

# 环境的类型：
# "APPDATA" 用户，低权限要求
# "ProgramData" 全局，高权限要求
EnvType = "APPDATA"  # or "ProgramData"


# ==================== 标准路径 ====================
# 获取系统的标准路径
class _StandardPaths:
    @staticmethod
    def GetStartMenu():
        """获取开始菜单路径"""
        return os.path.join(os.getenv(EnvType), "Microsoft", "Windows", "Start Menu")

    @staticmethod
    def GetStartup():
        """获取启动（开机自启）路径"""
        return os.path.join(_StandardPaths.GetStartMenu(), "Programs", "Startup")


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

    # 根据系统及硬件，判断最适合的渲染器类型
    @staticmethod
    def getOpenGLUse():
        import platform

        # 判断系统版本，若 >win10 则使用 GLES ，否则使用软渲染
        version = platform.version()
        if "." in version:
            ver = version.split(".")[0]
            if ver.isdigit() and int(ver) >= 10:
                return "AA_UseOpenGLES"
        return "AA_UseSoftwareOpenGL"

    # 键值转键名
    @staticmethod
    def getKeyName(key):
        return getKeyName(key)

    # 让系统运行一个程序，不堵塞当前进程
    @staticmethod
    def runNewProcess(path, args=""):
        subprocess.Popen(
            f'start "" "{path}" {args}',
            shell=True,
            # 确保在一个新的控制台窗口中运行，与当前进程完全独立。
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

    # 用系统默认应用打开一个文件或目录，不堵塞当前进程
    @staticmethod
    def startfile(path):
        os.startfile(path)
