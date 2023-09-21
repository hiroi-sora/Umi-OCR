# 程序的配置分为两部分，一部分是由qml引擎控制的主配置，必须启动qml才能访问。
# 而这里是第二部分的配置项，单独存放少量关键配置，可以在未启动qml之前访问。

import os
import json

_FileName = "./.pre_settings"

_Configs = {
    "i18n": "",  # 界面语言
    "opengl": "AA_UseDesktopOpenGL",  # 界面OpenGL渲染类型
}


def getValue(key):
    if key in _Configs:
        return _Configs[key]
    else:
        raise ValueError


def setValue(key, value):
    if key in _Configs:
        _Configs[key] = value
        writeConfigs()
    else:
        raise ValueError


def writeConfigs():
    with open(_FileName, "w", encoding="utf-8") as file:
        json.dump(_Configs, file, ensure_ascii=False, indent=4)


def readConfigs():
    try:
        with open(_FileName, "r") as file:
            data = json.load(file)
        for key in _Configs:
            _Configs[key] = data[key]
    except Exception:
        pass
