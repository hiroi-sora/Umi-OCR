# 通用工具

import re
import os
from PySide2.QtGui import QClipboard
from PySide2.QtCore import QFileInfo
from urllib.parse import unquote  # 路径解码
from PySide2.QtQml import QJSValue

Clipboard = QClipboard()  # 剪贴板

ImageSuf = [  # 合法图片后缀
    ".jpg",
    ".jpe",
    ".jpeg",
    ".jfif",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
]
DocSuf = [  # 合法文档后缀
    ".pdf",
    ".xps",
    ".epub",
    ".mobi",
    ".fb2",
    ".cbz",
]


# 传入文件名，检测是否含非法字符。没问题返回True
def allowedFileName(fn):
    pattern = r'[\\/:*?"<>|]'
    if re.search(pattern, fn):
        return False  # 转布尔值
    else:
        return True


# 路径是图片返回true
def isImg(path):
    return os.path.splitext(path)[-1].lower() in ImageSuf


# 路径是文档返回true
def isDoc(path):
    return os.path.splitext(path)[-1].lower() in DocSuf


def _findFiles(func, paths, isRecurrence):
    if type(paths) == QJSValue:
        paths = paths.toVariant()
    if type(paths) != list:
        print(f"[Error] _findFiles 传入：{paths}, {type(paths)}")
        return []
    filePaths = []
    for p in paths:
        if os.path.isfile(p) and func(p):  # 是文件，直接判断
            filePaths.append(os.path.abspath(p))
        elif os.path.isdir(p):  # 是目录
            if isRecurrence:  # 需要递归
                for root, dirs, files in os.walk(p):
                    for file in files:
                        if func(file):  # 收集子文件
                            filePaths.append(
                                os.path.abspath(os.path.join(root, file))
                            )  # 将路径转换为绝对路径
            else:  # 不递归读取子文件夹
                for file in os.listdir(p):
                    if os.path.isfile(os.path.join(p, file)) and func(file):
                        filePaths.append(os.path.abspath(os.path.join(p, file)))
    for i, p in enumerate(filePaths):  # 规范化正斜杠
        filePaths[i] = p.replace("\\", "/")
    return filePaths


# 传入路径列表，在路径中搜索图片。isRecurrence=True时递归搜索。
def findImages(paths, isRecurrence):
    return _findFiles(isImg, paths, isRecurrence)


# 传 入路径列表，在路径中搜索文档。isRecurrence=True时递归搜索。
def findDocs(paths, isRecurrence):
    return _findFiles(isDoc, paths, isRecurrence)


# 复制文本到剪贴板
def copyText(text):
    Clipboard.setText(text)


# QUrl列表 转 String列表
def QUrl2String(urls):
    resList = []
    for url in urls:
        if url.isLocalFile():
            u = unquote(url.toLocalFile())  # 解码路径
            if QFileInfo(u).exists():  # 检查路径是否真的存在
                resList.append(u)
    return resList


# 初始化配置项字典数值，等同于 Configs.qml 的 function initConfigDict
# 主要是为了补充type和default
def initConfigDict(dic):
    toDict = {}

    def handleConfigItem(config, key):  # 处理一个配置项
        # 类型：指定type
        if not config["type"] == "":
            if config["type"] == "file":  # 文件选择
                config["default"] = "" if not config["default"] is None else None
            elif config["type"] == "var":  # 缓存任意类型
                config["default"] = "" if not config["default"] is None else None
        # 类型：省略type
        else:
            if type(config["default"]) is bool:  # 布尔
                config["type"] = "boolean"
            elif "optionsList" in config:  # 枚举
                config["type"] = "enum"
                if len(config["optionsList"]) == 0:
                    print(f"处理配置项异常：{key}枚举列表为空。")
                    return
                if config["default"] is None:
                    config["default"] = config["optionsList"][0][0]
            elif type(config["default"]) is str:  # 文本
                config["type"] = "text"
            elif isinstance(config["default"], (int, float)):  # 数字
                config["type"] = "number"
            elif "btnsList" in config:  # 按钮组
                config["type"] = "buttons"
                return
            else:
                print("【Error】未知类型的配置项：" + key)
                return

    def handleConfigGroup(group, prefix=""):  # 处理一个配置组
        for key in group:
            config = group[key]
            if not type(config) is dict:
                continue
            # 补充空白参数
            if "type" not in config:  # 类型
                config["type"] = ""
            if "default" not in config:  # 默认值
                config["default"] = None
            # 记录完整key
            fullKey = prefix + key
            if config["type"] == "group":  # 若是配置项组，递归遍历
                handleConfigGroup(config, fullKey + ".")  # 前缀加深一层
                toDict[fullKey] = {
                    "title": config["title"],
                    "type": "group",
                    "advanced": config.advanced,
                }
            else:  # 若是配置项
                toDict[fullKey] = config
                handleConfigItem(config, fullKey)

    handleConfigGroup(dic)
    return toDict


# 整理 argd 参数字典，将 float 恢复 int 类型，如 12.0 → 12
def argdIntConvert(argd):
    for k, v in argd.items():
        if isinstance(v, float) and v.is_integer():
            argd[k] = int(v)
