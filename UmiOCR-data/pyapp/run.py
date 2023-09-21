import os
import sys
from .utils import pre_configs


# 启动主qml
def runQml():
    from PySide2.QtCore import Qt, QTranslator
    from PySide2.QtGui import QGuiApplication, QOpenGLContext
    from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

    import version as V
    from .tag_pages.tag_pages_connector import TagPageConnector  # 页面连接器
    from .mission.mission_connector import MissionConnector  # 任务连接器
    from .event_bus.pubsub_connector import PubSubConnector  # 发布/订阅连接器
    from .event_bus.key_mouse.key_mouse_connector import KeyMouseConnector  # 键盘/鼠标连接器
    from .utils.utils_connector import UtilsConnector  # 通用连接器
    from .utils.image_provider import PixmapProvider  # 图片提供器
    from .utils.i18n import I18n  # 语言

    # 0. 初始化环境变量。版本号，各路径。
    app_version = f"{V.MAJOR_VERSION}.{V.MINOR_VERSION}.{V.PATCH_VERSION}"
    if V.PRE_RELEASE:
        app_version += f"-{V.PRE_RELEASE}.{V.PRE_RELEASE_VERSION}"
    app_website = V.WEBSITE  # 网站
    app_path = os.environ.get("PYSTAND", "")  # 程序入口路径
    app_home = os.environ.get("PYSTAND_HOME", "")  # 程序入口目录
    app_working = os.environ["APP_WORKING"]  # 工作目录
    # 调试模式下，手动补充参数
    if not app_path:
        app_path = os.path.abspath("../Umi-OCR.exe")
        app_home = os.path.abspath("../")
    # 注入环境变量
    os.environ["APP_VERSION"] = app_version
    os.environ["APP_WEBSITE"] = app_website
    os.environ["APP_PATH"] = app_path
    os.environ["APP_HOME"] = app_home

    # TODO: 用户自行选择渲染方式！！！

    # 1. 全局参数设置
    # 启用 OpenGL 上下文之间的资源共享
    QGuiApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    # 启用OpenGLES以避免组件抖动问题
    QGuiApplication.setAttribute(Qt.AA_UseOpenGLES, True)
    # 启用高分屏自动缩放
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # 2. 启动qt
    qtApp = QGuiApplication(sys.argv)
    qtApp.setApplicationName(f"Umi-OCR")
    qtApp.setOrganizationName("hiroi-sora")
    qtApp.setOrganizationDomain(app_website)

    # 3. OpenGlES 兼容性检查
    if not QOpenGLContext.openGLModuleType() == QOpenGLContext.LibGLES:
        QGuiApplication.setAttribute(Qt.AA_UseOpenGLES, False)
        # TODO：记录本次结果，下次默认False
        msg = "检测到系统不支持OpenGLES，已设为禁用，将在下次启动生效。\n若本次运行中程序崩溃或报错，重新启动程序可能可以解决问题。\n\n"
        msg += "Detected that the system does not support OpenGLES and has been set to disabled. It will take effect on the next startup. \nIf the program crashes or reports an error during this run, restarting app may solve the problem."
        os.MessageBox(msg, info="Umi-OCR Warning")

    # 4. 注册Python类
    # 页面连接器
    qmlRegisterType(TagPageConnector, "TagPageConnector", 1, 0, "TagPageConnector")
    # 任务连接器
    qmlRegisterType(MissionConnector, "MissionConnector", 1, 0, "MissionConnector")
    # 发布/订阅连接器
    qmlRegisterType(PubSubConnector, "PubSubConnector", 1, 0, "PubSubConnector")
    # 键盘/鼠标连接器
    qmlRegisterType(KeyMouseConnector, "KeyMouseConnector", 1, 0, "KeyMouseConnector")
    # 通用连接器
    qmlRegisterType(UtilsConnector, "UtilsConnector", 1, 0, "UtilsConnector")

    # 5. 启动翻译
    trans = QTranslator()
    I18n.init(qtApp, trans)

    # 6. 启动qml引擎
    engine = QQmlApplicationEngine()
    engine.addImportPath("./.site-packages/PySide2/qml")  # 相对路径重新导入包
    engine.addImageProvider("pixmapprovider", PixmapProvider)  # 注册图片提供器
    rootContext = engine.rootContext()  # 注册常量
    rootContext.setContextProperty("APP_VERSION", app_version)
    rootContext.setContextProperty("APP_WEBSITE", app_website)
    engine.load(f"res/qml/Main.qml")  # 通过本地文件启动
    # engine.load(f"qrc:/qml/Main.qml")  # 通过qrc启动
    if not engine.rootObjects():
        sys.exit(0)
    res = qtApp.exec_()
    print("== APP退出！")
    sys.exit(res)


def main():
    pre_configs.readConfigs()  # 初始化预配置项
    runQml()  # 启动qml


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
