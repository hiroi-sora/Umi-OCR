import os
import sys

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt, QCoreApplication, QObject, QTranslator  # 翻译


def main():

    # 启用OpenGL渲染，减少窗口闪烁
    QGuiApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)

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
