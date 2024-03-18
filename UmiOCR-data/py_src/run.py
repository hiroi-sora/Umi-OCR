# Umi-OCR
# OCR software, free and offline. 开源、免费的离线OCR软件。
# Website - https://github.com/hiroi-sora/Umi-OCR
# Author - hiroi-sora
#
# You are free to use, modify, and distribute Umi-OCR, but it must include
# the original author's copyright statement and the following license statement.
# 您可以免费地使用、修改和分发 Umi-OCR ，但必须包含原始作者的版权声明和下列许可声明。
"""
Copyright (c) 2023 hiroi-sora

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


"""
=========================================
========== Umi-OCR 软件启动入口 ==========
=========================================

说明：
本文件必须在运行环境初始化之后调用。
负责 Umi-OCR 的信息初始化并启动主事件循环。
"""

import os
import sys
import site


# 启动主qml。工作路径必须为 UmiOCR-data
def runQml(engineAddImportPath):
    # ==================== 0. 导入包 ====================
    from PySide2.QtCore import Qt, QTranslator
    from PySide2.QtGui import QGuiApplication
    from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

    from umi_about import UmiAbout  # 项目信息
    from .utils import app_opengl  # 渲染器

    # ==================== 1. 全局参数设置 ====================
    # 启用 OpenGL 上下文之间的资源共享
    QGuiApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    # 启用高分屏自动缩放
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # 初始化渲染器
    app_opengl.initOpengl()

    # ==================== 2. 启动qt ====================
    qtApp = QGuiApplication(sys.argv)
    qtApp.setApplicationName(UmiAbout["name"])
    qtApp.setOrganizationName(UmiAbout["authors"][0]["name"])
    qtApp.setOrganizationDomain(UmiAbout["url"]["home"])

    # ==================== 3. OpenGlES 兼容性检查 ====================
    app_opengl.checkOpengl()

    # ==================== 4. 注册连接器Python类 ====================
    from .tag_pages.tag_pages_connector import TagPageConnector  # 页面连接器
    from .mission.mission_connector import MissionConnector  # 任务连接器
    from .mission.doc_preview_connector import DocPreviewConnector  # 文档预览连接器
    from .event_bus.pubsub_connector import PubSubConnector  # 发布/订阅连接器
    from .event_bus.key_mouse.key_mouse_connector import (  # 键盘/鼠标连接器
        KeyMouseConnector,
    )
    from .plugins_controller.plugins_connector import PluginsConnector  # 插件连接器
    from .utils.utils_connector import UtilsConnector  # 通用连接器
    from .utils.global_configs_connector import GlobalConfigsConnector  # 全局配置连接器
    from .utils.theme_connector import ThemeConnector  # 主题连接器
    from .image_controller.image_connector import ImageConnector  # 图片处理连接器
    from .image_controller.image_provider import PixmapProvider  # 图片提供器
    from .utils.i18n_configs import I18n  # 语言

    qmlRegisterType(TagPageConnector, "TagPageConnector", 1, 0, "TagPageConnector")
    qmlRegisterType(MissionConnector, "MissionConnector", 1, 0, "MissionConnector")
    qmlRegisterType(PubSubConnector, "PubSubConnector", 1, 0, "PubSubConnector")
    qmlRegisterType(KeyMouseConnector, "KeyMouseConnector", 1, 0, "KeyMouseConnector")
    qmlRegisterType(UtilsConnector, "UtilsConnector", 1, 0, "UtilsConnector")
    qmlRegisterType(PluginsConnector, "PluginsConnector", 1, 0, "PluginsConnector")
    qmlRegisterType(ThemeConnector, "ThemeConnector", 1, 0, "ThemeConnector")
    qmlRegisterType(ImageConnector, "ImageConnector", 1, 0, "ImageConnector")
    qmlRegisterType(
        GlobalConfigsConnector, "GlobalConfigsConnector", 1, 0, "GlobalConfigsConnector"
    )
    qmlRegisterType(
        DocPreviewConnector, "DocPreviewConnector", 1, 0, "DocPreviewConnector"
    )

    # ==================== 5. 启动翻译 ====================
    trans = QTranslator()
    I18n.init(qtApp, trans)

    # ==================== 6. 启动qml引擎 ====================
    engine = QQmlApplicationEngine()
    if engineAddImportPath:
        engine.addImportPath(engineAddImportPath)  # 相对路径重新导入包
    engine.addImageProvider("pixmapprovider", PixmapProvider)  # 注册图片提供器
    rootContext = engine.rootContext()  # 注册常量
    rootContext.setContextProperty("UmiAbout", UmiAbout)
    engine.load("qt_res/qml/Main.qml")  # 通过本地文件启动
    if not engine.rootObjects():
        return 1
    res = qtApp.exec_()
    if res != 0:
        msg = f"Umi-OCR 异常退出。代码：{str(res)}\nUmi-OCR exited abnormally. Code: {str(res)}"
        os.MessageBox(msg)
    print("###  QML引擎关闭！")


def main(app_path, engineAddImportPath=""):
    """
    `app_path`: 程序入口文件 路径\n
    `engineAddImportPath`: 可选，qml包路径\n
    """
    # 初始化运行信息
    site.addsitedir("./py_src/imports")  # 自定义库添加到搜索路径
    import umi_about
    from .utils import pre_configs
    from .server.cmd_client import initCmd

    if not umi_about.init(app_path):  # 初始化版本信息，失败则结束运行
        sys.exit(0)
    # 安装某些软件时可能在系统中写入 QMLSCENE_DEVICE 环境变量，影响本软件的渲染方式，因此屏蔽该环境变量
    if "QMLSCENE_DEVICE" in os.environ:
        del os.environ["QMLSCENE_DEVICE"]

    pre_configs.readConfigs()  # 初始化预配置项
    if not initCmd():  # 初始化命令行，如果已有Umi-OCR在运行则结束运行
        sys.exit(0)
    runQml(engineAddImportPath)  # 启动qml
    sys.exit(0)
