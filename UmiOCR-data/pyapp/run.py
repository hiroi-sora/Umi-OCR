import os
import sys
from .utils import pre_configs
from .server.cmd_client import initCmd


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
    from .utils.global_configs_connector import GlobalConfigsConnector  # 全局配置连接器
    from .utils.image_provider import PixmapProvider  # 图片提供器
    from .utils.i18n import I18n  # 语言
    from .utils import app_opengl  # 渲染器

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

    # 1. 全局参数设置
    # 启用 OpenGL 上下文之间的资源共享
    QGuiApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    # 启用高分屏自动缩放
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # 初始化渲染器
    app_opengl.initOpengl()

    # 2. 启动qt
    qtApp = QGuiApplication(sys.argv)
    qtApp.setApplicationName(f"Umi-OCR")
    qtApp.setOrganizationName("hiroi-sora")
    qtApp.setOrganizationDomain(app_website)

    # 3. OpenGlES 兼容性检查
    app_opengl.checkOpengl()

    # 4. 注册连接器Python类
    qmlRegisterType(TagPageConnector, "TagPageConnector", 1, 0, "TagPageConnector")
    qmlRegisterType(MissionConnector, "MissionConnector", 1, 0, "MissionConnector")
    qmlRegisterType(PubSubConnector, "PubSubConnector", 1, 0, "PubSubConnector")
    qmlRegisterType(KeyMouseConnector, "KeyMouseConnector", 1, 0, "KeyMouseConnector")
    qmlRegisterType(UtilsConnector, "UtilsConnector", 1, 0, "UtilsConnector")
    qmlRegisterType(
        GlobalConfigsConnector, "GlobalConfigsConnector", 1, 0, "GlobalConfigsConnector"
    )

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
        return 0
    res = qtApp.exec_()
    print("###  QML引擎关闭！")
    return res


def main():
    pre_configs.readConfigs()  # 初始化预配置项
    if not initCmd():  # 初始化命令行，如果已有Umi-OCR在运行则结束运行
        sys.exit(0)
    res = runQml()  # 启动qml
    sys.exit(res)
