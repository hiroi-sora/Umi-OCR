# 软件渲染选项

from PySide2.QtGui import QGuiApplication, QOpenGLContext
from PySide2.QtCore import Qt
import os

from . import pre_configs
from ..platform import Platform

_GLDict = {
    "AA_UseDesktopOpenGL": Qt.AA_UseDesktopOpenGL,
    "AA_UseOpenGLES": Qt.AA_UseOpenGLES,
    "AA_UseSoftwareOpenGL": Qt.AA_UseSoftwareOpenGL,
}
_Opt = ""


def initOpengl():
    global _Opt
    opt = getOpengl()
    if opt not in _GLDict:
        opt = Platform.getOpenGLUse()
        setOpengl(opt)
    QGuiApplication.setAttribute(_GLDict[opt], True)
    _Opt = opt


def checkOpengl():
    global _Opt
    if _Opt == "AA_UseOpenGLES":  # GLES需要检查，有些win7不支持
        if not QOpenGLContext.openGLModuleType() == QOpenGLContext.LibGLES:
            QGuiApplication.setAttribute(Qt.AA_UseOpenGLES, False)
            _Opt = "AA_UseSoftwareOpenGL"  # 既然不支持opengl，那就软渲染吧
            setOpengl(_Opt)
            msg = "当前系统不支持OpenGLES，已禁用此渲染器。\n若本次运行中程序崩溃或报错，请重新启动程序。\n\n"
            msg += "The current system does not support OpenGLES and has disabled the program from using this renderer. \nIf there are crashes or errors during this run, please restarting the program."
            os.MessageBox(msg, type_="warning")


def setOpengl(opt):
    if opt not in _GLDict:
        raise ValueError
    pre_configs.setValue("opengl", opt)


def getOpengl():
    return pre_configs.getValue("opengl")


# OpenGL渲染模式
# 启用 OpenGL 上下文之间的资源共享
# QGuiApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
# 渲染模式，【减少窗口调整大小时内容的抖动】
# 方式一：启用OpenGL软件渲染。性能最差，CPU占用率大幅提升，效果最好。
# QGuiApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)
# 方式二：使用 桌面 OpenGL（例如 opengl32.dll 或 libGL.so）。性能最好，效果较差。
# QGuiApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)
# 方式三：使用 OpenGL ES 2.0 或更高版本，用d3d接口抽象成Opengl。性能和效果都很好。但兼容性很差：
# 1. ColorOverlay必须开启cache，否则无法渲染透明层。
# 2. 需要系统安装dx9和OpenGL3。虚拟机中可能无法使用。需要检查兼容性！！！
# 必须做兼容性判定，兼容时才启用AA_UseOpenGLES。
# QGuiApplication.setAttribute(Qt.AA_UseOpenGLES, True)
