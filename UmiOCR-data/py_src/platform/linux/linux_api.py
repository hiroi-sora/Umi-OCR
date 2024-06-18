# ==============================================
# =============== Linux系统API ===============
# ==============================================

import os
import shlex
import subprocess
from .key_translator import getKeyName


# ==================== 快捷方式 ====================
class _Shortcut:
    # 创建快捷方式，返回成功与否的字符串。position取值：
    # desktop 桌面
    # startMenu 开始菜单
    # startup 开机自启
    @staticmethod
    def createShortcut(position):
        from umi_about import UmiAbout  # 项目信息

        lnkName = "Umi-OCR"
        appPath = UmiAbout["app"]["path"]
        # TODO
        return f"[Error] Linux 尚未实现 {position} 快捷方式的创建！"

    @staticmethod  # 删除快捷方式
    def deleteShortcut(position):
        appName = "Umi-OCR"
        # TODO
        return 0




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
    # 快捷方式。接口： createShortcut deleteShortcut
    # 参数：快捷方式位置， desktop startMenu startup
    Shortcut = _Shortcut()

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
