# 程序的配置分为两部分，一部分是由qml引擎控制的主配置，必须启动qml才能访问。
# 而这里是第二部分的配置项，单独存放少量关键配置，可以在未启动qml之前访问。

import os
import json

_FileName = "./.pre_settings"

_Configs = {
    "i18n": "",  # 界面语言
    "opengl": "",  # 界面OpenGL渲染类型
    "server_port": 1224,  # 服务端口号
    "last_pid": -1,  # 最后一次运行时的进程号
    "last_ptime": -1,  # 最后一次运行时的进程创建时间
}

_Errors = {}  # 记录读写预配置文件的异常情况


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
    global _Errors
    try:
        with open(_FileName, "w", encoding="utf-8") as file:
            json.dump(_Configs, file, ensure_ascii=False, indent=4)
    except PermissionError:
        _Errors[
            "Write PermissionError"
        ] = "权限不足，无法写入配置文件。\nInsufficient permissions, unable to write to the configuration file."
    except Exception as e:
        _Errors[
            "Write Error"
        ] = f"无法写入配置文件。\nUnable to write to the configuration file: {e}"


def readConfigs():
    global _Errors
    if not os.path.exists(_FileName):
        return
    try:
        with open(_FileName, "r") as file:
            data = json.load(file)
        for key in _Configs:
            _Configs[key] = data[key]
    except PermissionError:
        _Errors[
            "Write PermissionError"
        ] = "权限不足，无法读取配置文件。\nInsufficient permissions, unable to read to the configuration file."
    except Exception as e:
        _Errors[
            "Write Error"
        ] = f"无法读取配置文件。\nUnable to read to the configuration file: {e}"


# 返回异常情况字符串
def getErrorStr():
    global _Errors
    err = ""
    if _Errors:
        for e in _Errors.values():
            err += e + "\n"
    return err
