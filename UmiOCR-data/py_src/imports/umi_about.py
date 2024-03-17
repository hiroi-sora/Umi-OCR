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
=========================================================
=============== 为全局提供 Umi-OCR 关于信息 ===============
=========================================================

在任意python文件中访问：
from umi_about import UmiAbout
UmiAbout["fullname"]

在任意qml文件中访问：
UmiAbout.fullname
"""

import os
from json import load

UmiAbout = None


# 初始化时调用一次
def init(app_path=""):
    """
    `app_path`: 程序入口文件 路径\n
    """
    global UmiAbout
    # 读取配置
    try:
        with open("about.json", "r", encoding="utf-8") as file:
            u = load(file)
    except Exception as e:
        os.MessageBox(f"[Error] 无法读取配置 about.json 。\n{e}")
        return False
    # 完整版本号
    v = f'{u["version"]["major"]}.{u["version"]["minor"]}.{u["version"]["patch"]}'
    if u["version"]["prerelease"]:
        v += f'-{u["version"]["prerelease"]}.{u["version"]["prereleaseNumber"]}'
    u["version"]["string"] = v
    # 全名
    u["fullname"] = f'{u["name"]} v{v}'
    # 入口信息
    if app_path:
        app_path = os.path.abspath(app_path)
        app_home = os.path.dirname(app_path)
    else:
        app_path = ""
        app_home = ""
    u["app"] = {
        "path": app_path,
        "home": app_home,
    }
    UmiAbout = u
    return True
