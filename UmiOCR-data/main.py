# =====================================
# ========== Umi-OCR 启动入口 ==========
# =====================================

# 耗时统计：
# runtime/python.exe -X importtime main.py

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

    # def except_hook(cls, exception, traceback):
    #     sys.__excepthook__(cls, exception, traceback)
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
    os.environ["APP_WORKING"] = working
    os.chdir(working)  # 重新设定工作目录（不在最顶层，而在UmiOCR-data文件夹下）
    for n in [".", "site-packages"]:  # 将模块目录添加到 Python 搜索路径中
        path = os.path.abspath(os.path.join(working, n))
        if os.path.exists(path):
            site.addsitedir(path)


def runScript():
    # 默认启动脚本
    from py_src.run import main

    main()


if __name__ == "__main__":
    initRuntimeEnvironment(__file__)  # 初始化运行环境
    runScript()  # 启动脚本
