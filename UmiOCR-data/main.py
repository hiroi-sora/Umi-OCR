# =====================================
# ========== Umi-OCR 启动入口 ==========
# =====================================

import os
import sys
import site


def initRuntimeEnvironment(startup_script):
    """初始化运行环境"""

    # 重定向输出流到控制台窗口
    try:
        fd = os.open("CONOUT$", os.O_RDWR | os.O_BINARY)
        fp = os.fdopen(fd, "w")
        sys.stdout = fp
        sys.stderr = fp
    except Exception as e:
        fp = open(os.devnull, "w")
        sys.stdout = fp
        sys.stderr = fp

    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)

    # sys.excepthook = except_hook

    # 定义一个最简单的消息弹窗
    def MessageBox(msg, info="Umi-OCR Message"):
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, str(msg), str(info), 0)
        return 0

    os.MessageBox = MessageBox

    # 初始化工作目录和Python搜索路径
    script = os.path.abspath(startup_script)  # 启动脚本.py的路径
    working = os.path.dirname(script)  # 工作目录
    os.chdir(working)  # 重新设定工作目录（不在最顶层，而在UmiOCR-data文件夹下）
    for n in [".", ".site-packages"]:  # 将模块目录添加到 Python 搜索路径中
        path = os.path.abspath(os.path.join(working, n))
        if os.path.exists(path):
            site.addsitedir(path)

    # 初始化Qt搜索路径，采用相对路径，避免中文路径编码问题
    try:
        from PySide2.QtCore import QCoreApplication

        QCoreApplication.addLibraryPath("./.site-packages/PySide2/plugins")
    except Exception as e:
        print(e)
        os.MessageBox(f"Qt plugins 目录导入失败！\nQt plugins directory import failed!\n\n{e}")
        os._exit(1)

    # 初始化环境变量
    import version as V

    APP_NAME = V.APP_NAME
    APP_VERSION = f"{V.MAJOR_VERSION}.{V.MINOR_VERSION}.{V.PATCH_VERSION}"
    if V.PRE_RELEASE:
        APP_VERSION += f"-{V.PRE_RELEASE}.{V.PRE_RELEASE_VERSION}"
    APP_PATH = os.environ.get("PYSTAND", "")
    APP_HOME = os.environ.get("PYSTAND_HOME", "")
    APP_WORKING = working
    # 调试模式下，手动补充参数
    if not APP_PATH:
        APP_PATH = os.path.abspath("../Umi-OCR.exe")
        APP_HOME = os.path.abspath("../")
    # 注入环境变量
    os.environ["APP_NAME"] = APP_NAME
    os.environ["APP_VERSION"] = APP_VERSION
    os.environ["APP_PATH"] = APP_PATH
    os.environ["APP_HOME"] = APP_HOME
    os.environ["APP_WORKING"] = APP_WORKING

    print("初始化Python运行环境完成！")


if __name__ == "__main__":
    initRuntimeEnvironment(__file__)  # 初始化运行环境

    # 必须初始化运行环境后，再导入自定义包
    from pyapp.run import main

    main()
