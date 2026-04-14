# ==============================================
# =============== macOS 系统API ===============
# ==============================================

import os
import shlex
import subprocess
from PySide2.QtCore import QStandardPaths as Qsp

from umi_log import logger
from umi_about import UmiAbout
from .key_translator import getKeyName


# ==================== 快捷方式 ====================
class _Shortcut:
    @staticmethod
    def _getPath(position):
        # 桌面
        if position == "desktop":
            return Qsp.writableLocation(Qsp.DesktopLocation)
        # 应用程序（/Applications 或 ~/Applications）
        elif position == "startMenu":
            return Qsp.writableLocation(Qsp.ApplicationsLocation)
        # 开机自启：macOS 使用 LaunchAgents
        elif position == "startup":
            return os.path.expanduser("~/Library/LaunchAgents")

    # 创建快捷方式（macOS 符号链接），返回成功与否的字符串。position取值：
    # desktop 桌面
    # startMenu 应用程序
    # startup 开机自启
    @staticmethod
    def createShortcut(position):
        lnkName = UmiAbout["name"]
        appPath = UmiAbout["app"]["path"]
        appDir = UmiAbout["app"]["dir"]
        if not appPath:
            return (
                f"[Error] 未找到程序入口文件。请尝试手动创建快捷方式。\n"
                f"[Error] App path not exist. Please try creating a shortcut manually.\n\n{appPath}"
            )

        if position == "startup":
            # macOS 开机自启通过 LaunchAgent plist 实现
            return _Shortcut._createLaunchAgent(lnkName, appPath, appDir)

        # desktop / startMenu：创建符号链接
        try:
            lnkDir = _Shortcut._getPath(position)
            lnkPathBase = os.path.join(lnkDir, lnkName)
            lnkPath = lnkPathBase
            i = 1
            while os.path.exists(lnkPath):
                lnkPath = f"{lnkPathBase} ({i})"
                i += 1
            os.symlink(appPath, lnkPath)
            logger.info(f"创建快捷方式： {lnkPath}")
            return "[Success]"
        except Exception as e:
            return (
                f"[Error] 创建快捷方式失败。\n"
                f"[Error] Failed to create shortcut.\n {lnkPath}: {e}"
            )

    @staticmethod
    def _createLaunchAgent(lnkName, appPath, appDir):
        """创建 macOS LaunchAgent plist 实现开机自启"""
        plistName = f"com.umi-ocr.{lnkName}.plist"
        plistDir = _Shortcut._getPath("startup")
        os.makedirs(plistDir, exist_ok=True)
        plistPath = os.path.join(plistDir, plistName)

        plistContent = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.umi-ocr.{lnkName}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{appPath}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{appDir}</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        try:
            with open(plistPath, "w") as f:
                f.write(plistContent)
            logger.info(f"创建开机自启 LaunchAgent： {plistPath}")
            return "[Success]"
        except Exception as e:
            return (
                f"[Error] 创建开机自启失败。\n"
                f"[Error] Failed to create LaunchAgent.\n {plistPath}: {e}"
            )

    # 删除快捷方式，返回删除文件的个数
    @staticmethod
    def deleteShortcut(position):
        try:
            appName = UmiAbout["name"]
            lnkDir = _Shortcut._getPath(position)
        except Exception:
            logger.error("无法获取应用信息", exc_info=True, stack_info=True)
            return 0

        num = 0
        if not os.path.isdir(lnkDir):
            return 0

        for fileName in os.listdir(lnkDir):
            try:
                lnkPath = os.path.join(lnkDir, fileName)
                if position == "startup":
                    # LaunchAgent plist 文件
                    if appName.lower() in fileName.lower() and fileName.endswith(
                        ".plist"
                    ):
                        os.remove(lnkPath)
                        num += 1
                        logger.info(f"删除开机自启： {lnkPath}")
                else:
                    # 符号链接
                    if os.path.islink(lnkPath) and appName in fileName:
                        os.remove(lnkPath)
                        num += 1
                        logger.info(f"删除快捷方式： {lnkPath}")
            except Exception:
                logger.error(
                    f"删除快捷方式失败。 lnkPath: {lnkPath}",
                    exc_info=True,
                    stack_info=True,
                )
                continue
        return num


# ==================== 硬件控制 ====================
class _HardwareCtrl:
    # 关机
    @staticmethod
    def shutdown():
        os.system(
            'osascript -e \'tell application "System Events" to shut down\''
        )

    # 休眠（macOS 使用 pmset sleepnow）
    @staticmethod
    def hibernate():
        os.system("pmset sleepnow")


# ==================== 对外接口 ====================
class Api:
    # 快捷方式。接口： createShortcut deleteShortcut
    # 参数：快捷方式位置， desktop startMenu startup
    Shortcut = _Shortcut()

    # 硬件控制。接口： shutdown hibernate
    HardwareCtrl = _HardwareCtrl()

    # 根据系统及硬件，判断最适合的渲染器类型
    @staticmethod
    def getOpenGLUse():
        # macOS: Qt6 uses RHI which auto-selects Metal on Apple Silicon.
        # Desktop OpenGL avoids the GLES compatibility check that would
        # show a spurious warning dialog (macOS doesn't expose GLES).
        return "AA_UseDesktopOpenGL"

    # 键值转键名
    @staticmethod
    def getKeyName(key):
        return getKeyName(key)

    # 让系统运行一个程序，不堵塞当前进程
    @staticmethod
    def runNewProcess(path, args=""):
        command_line = [path] + shlex.split(args)
        subprocess.Popen(command_line)

    # 用系统默认应用打开一个文件或目录，不堵塞当前进程
    @staticmethod
    def startfile(path):
        subprocess.Popen(["open", path])

    # 检查 macOS 屏幕录制权限
    @staticmethod
    def checkScreenRecordingPermission():
        """检查并请求 macOS 屏幕录制权限。返回 True 表示已授权。"""
        try:
            import ctypes
            import ctypes.util

            cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreGraphics"))
            cg.CGPreflightScreenCaptureAccess.restype = ctypes.c_bool
            if not cg.CGPreflightScreenCaptureAccess():
                # 请求权限（触发系统弹窗）
                cg.CGRequestScreenCaptureAccess.restype = ctypes.c_bool
                cg.CGRequestScreenCaptureAccess()
                return False
            return True
        except Exception:
            return True  # 无法检查时默认允许（旧版 macOS）

    # 检查 macOS 辅助功能权限
    @staticmethod
    def checkAccessibilityPermission():
        """检查 macOS 辅助功能权限。返回 True 表示已授权。"""
        try:
            import ctypes
            import ctypes.util

            lib = ctypes.cdll.LoadLibrary(
                ctypes.util.find_library("ApplicationServices")
            )
            lib.AXIsProcessTrusted.restype = ctypes.c_bool
            return lib.AXIsProcessTrusted()
        except Exception:
            return True  # 无法检查时默认允许
