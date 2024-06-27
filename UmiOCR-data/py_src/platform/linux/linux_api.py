# ==============================================
# =============== Linux系统API ===============
# ==============================================

import os
import shlex
import subprocess
from PySide2.QtCore import QStandardPaths as Qsp

from umi_about import UmiAbout


# ==================== 快捷方式 ====================
class _Shortcut:
    @staticmethod
    def _getPath(position):  # 获取路径
        # 桌面
        if position == "desktop":
            return Qsp.writableLocation(Qsp.DesktopLocation)
        # 开始菜单
        if position == "startMenu":
            return Qsp.writableLocation(Qsp.ApplicationsLocation)
        # 开机自启 TODO
        elif position == "startup":
            raise ValueError("Linux 暂不支持自动添加开机自启。请手动设置。")

    # 创建快捷方式，返回成功与否的字符串。position取值：
    # desktop 桌面
    # startMenu 开始菜单
    # startup 开机自启
    @staticmethod
    def createShortcut(position):
        if position == "startup":  # TODO
            return "[Warning] Linux 暂不支持自动添加开机自启。请手动设置。\nAutomatically adding startup functions is not supported at this time. Please set it manually."
        try:
            lnkName = UmiAbout["name"]
            appPath = UmiAbout["app"]["path"]
            appDir = UmiAbout["app"]["dir"]
            if not appPath:
                return f"[Error] 未找到程序入口文件。请尝试手动创建快捷方式。\n[Error] Umi-OCR app path not exist. Please try creating a shortcut manually.\n\n{appPath}"

            lnkPathBase = _Shortcut._getPath(position)
            lnkPathBase = os.path.join(lnkPathBase, lnkName)
            lnkPath = lnkPathBase + ".desktop"
            i = 1
            while os.path.exists(lnkPath):  # 快捷方式已存在
                lnkPath = lnkPathBase + f" ({i}).desktop"  # 添加序号
                i += 1
        except Exception as e:
            return f"[Error] 无法获取应用信息。\n[Error] Unable to obtain application information.\n\n{e}"

        # 快捷方式 文件内容
        desktop_entry = f"""
[Desktop Entry]
Version={UmiAbout["version"]["string"]}
Type=Application
Name={lnkName}
Exec={appPath}
Path={appDir}
Icon={appDir}/UmiOCR-data/qt_res/images/icons/umiocr.ico
Terminal=false
"""

        try:
            with open(lnkPath, "w") as f:
                f.write(desktop_entry)
            os.chmod(lnkPath, 0o755)  # 赋予执行权限
            print(f"创建快捷方式： {lnkPath}")
            return "[Success]"
        except Exception as e:
            return f"[Error] 创建快捷方式失败。\n[Error] Failed to create shortcut.\n {lnkPath}: {e}"

    # 删除快捷方式，返回删除文件的个数
    @staticmethod
    def deleteShortcut(position):
        try:
            appName = UmiAbout["name"]
            lnkDir = _Shortcut._getPath(position)
        except Exception as e:
            print(f"[Error] 无法获取应用信息。\n[Error] Unable to obtain application information.\n\n{e}")
            return 0

        num = 0
        for fileName in os.listdir(lnkDir):
            try:
                lnkPath = os.path.join(lnkDir, fileName)
                if not os.path.isfile(lnkPath):  # 排除非文件
                    continue
                if fileName.startswith(appName) and fileName.endswith(".desktop"):
                    os.remove(lnkPath)
                    num += 1
                    print(f"删除快捷方式： {lnkPath}")
            except Exception as e:
                print(f"[Error] 删除快捷方式失败 {lnkPath}: {e}")
                continue
        return num


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
        # 传入 pynput 按键事件对象，返回键名字符串
        if not isinstance(key, str):
            key = str(key)
        if not key:  # 错误，未获取键值
            return "unknown"
        if key.startswith("'") and key.endswith("'"): # 去除自带引号
            key = key[1:-1]
        if key.startswith("Key."):  # 修饰建
            key = key[4:]
        if not key: # 再检查一次
            return "unknown"
        return key

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
