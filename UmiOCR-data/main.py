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
======================================================
========== Umi-OCR Windows 运行环境初始化入口 ==========
======================================================

说明：
本文件负责 Windows + PyStand 运行环境的初始化，主要涉及：
- 创建底层弹窗接口 os.MessageBox
- 重定向标准输入输出流
- 指定工作目录为 "/UmiOCR-data"
- 添加Python库搜索目录 "site-packages"
- 添加PySide2插件搜索目录 "PySide2/plugins"

环境初始化后，调用正式入口 py_src/run.py 启动软件。

耗时分析：
runtime/python.exe -X importtime main.py
"""


import os
import sys
import site
import traceback
import subprocess


def MessageBox(msg, type_="error"):
    info = "Umi-OCR Message"
    if type_ == "error":
        info = "【错误】 Umi-OCR Error"
    elif type_ == "warning":
        info = "【警告】 Umi-OCR Warning"
    try:
        # 通过 ctypes 发起弹窗
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, str(msg), str(info), 0)
    except Exception:
        # 部分系统，连ctypes也用不了。转为在新的控制台窗口中打印信息。
        msg_cmd = (
            msg.replace("^", "^^")
            .replace("&", "^&")
            .replace("<", "^<")
            .replace(">", "^>")
            .replace("|", "^|")
            .replace("\n\n", "___")
            .replace("\n", "___")
        )
        subprocess.Popen(["start", "cmd", "/k", f"echo {info}: {msg_cmd}"], shell=True)
    return 0


os.MessageBox = MessageBox


def initRuntimeEnvironment():
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

    # 初始化工作目录和Python搜索路径
    script = os.path.abspath(__file__)  # 启动脚本.py的路径
    cwd = os.path.dirname(script)  # 工作目录
    os.chdir(cwd)  # 重新设定工作目录（不在最顶层，而在 UmiOCR-data 文件夹下）
    for n in [".", "site-packages"]:  # 将模块目录添加到 Python 搜索路径中
        path = os.path.abspath(os.path.join(cwd, n))
        if os.path.exists(path):
            site.addsitedir(path)
    # 初始化Qt搜索路径为相对路径，避免上层目录存在中文编码
    from PySide2.QtCore import QCoreApplication

    QCoreApplication.addLibraryPath("./site-packages/PySide2/plugins")


if __name__ == "__main__":
    try:
        initRuntimeEnvironment()  # 初始化运行环境
    except Exception as e:
        err = traceback.format_exc()
        MessageBox("Failed to initialize running environment!\n\n" + err)
        sys.exit(0)
    try:
        # 获取 pystand.exe 记录的程序入口环境变量
        app_path = os.environ.get("PYSTAND", "")
        # 启动正式入口
        from py_src.run import main

        main(app_path=app_path, engineAddImportPath="./site-packages/PySide2/qml")
    except Exception as e:
        err = traceback.format_exc()
        MessageBox("Failed to startup main program!\n\n" + err)
        sys.exit(0)
