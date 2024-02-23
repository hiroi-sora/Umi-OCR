# =====================================
# ========== Umi-OCR 启动入口 ==========
# =====================================

# 耗时统计：
# runtime/python.exe -X importtime main.py

import os
import sys
import site


def MessageBox(msg, type="error"):
    import ctypes

    info = "Umi-OCR Message"
    if type == "error":
        info = "【错误】 Umi-OCR Error"
    elif type == "warning":
        info = "【警告】 Umi-OCR Warning"
    ctypes.windll.user32.MessageBoxW(None, str(msg), str(info), 0)
    return 0


os.MessageBox = MessageBox


def initRuntimeEnvironment(startup_script):
    """初始化运行环境"""

    # 尝试获取控制台的输出对象
    try:
        fd = os.open("CONOUT$", os.O_RDWR | os.O_BINARY)
        fp = os.fdopen(fd, "w", encoding="utf-8")
    except Exception as e:
        fp = open(os.devnull, "w", encoding="utf-8")
    # 输出流不存在时，重定向到控制台
    if not sys.stdout:
        sys.stdout = fp
    if not sys.stderr:
        sys.stderr = fp
    # def except_hook(cls, exception, traceback):
    #     sys.__excepthook__(cls, exception, traceback)
    # sys.excepthook = except_hook

    # 安装某些软件时可能在系统中写入 QMLSCENE_DEVICE 环境变量，影响本软件的渲染方式，因此屏蔽该环境变量
    if "QMLSCENE_DEVICE" in os.environ:
        del os.environ["QMLSCENE_DEVICE"]
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
    try:
        initRuntimeEnvironment(__file__)  # 初始化运行环境
    except Exception as e:
        MessageBox("初始化运行环境失败 !\n\n" + str(e))
        sys.exit(0)
    try:
        runScript()  # 启动脚本
    except Exception as e:
        MessageBox("主程序启动失败 !\n\n" + str(e))
