import os
import sys

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt, QCoreApplication, QObject, QTranslator  # 翻译


def main():

    # 启用 OpenGL 上下文之间的资源共享
    QGuiApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    # 【减少窗口调整大小时内容的抖动】
    # 方式一：启用OpenGL软件渲染，减少窗口闪烁（CPU占用率大幅提高！慎用）
    # QGuiApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)
    # 方式二：使用 OpenGL ES 2.0 或更高版本，用d3d接口抽象成Opengl。性能好，效果好，ColorOverlay必须开启cache否则无法渲染透明层。
    QGuiApplication.setAttribute(Qt.AA_UseOpenGLES, True)
    # 方式三：使用 桌面 OpenGL（例如 opengl32.dll 或 libGL.so）。性能最好，效果较差。
    # QGuiApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)

    # 启动qt
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Umi-OCR")
    app.setOrganizationName("hiroi-sora")
    app.setOrganizationDomain("hiroi-sora.com")

    # 启动翻译
    # trans = QTranslator()
    # if trans.load(r"翻译文1件.qm"):
    #     app.installTranslator(trans)  # 安装翻译器
    # else:
    #     print("翻译文件安装失败！")

    # 启动qml引擎
    engine = QQmlApplicationEngine()
    engine.addImportPath("./.site-packages/PySide2/qml")  # 相对路径重新导入包
    engine.load(f"res/qml/Main.qml")  # 通过本地文件启动
    # engine.load(f"qrc:/qml/Main.qml")  # 通过qrc启动

    if not engine.rootObjects():
        sys.exit(0)
    sys.exit(app.exec_())
