# ============================================
# =============== 文件查找/加载 ===============
# ============================================
# 从指定路径中，查找符合的文件

import re
import os
import time
from PySide2.QtQml import QJSValue
from typing import List

from ..event_bus.pubsub_service import PubSubService  # 发布事件
from ..mission.mission_doc import MissionDOC, DocSuf
from ..mission.mission_ocr import ImageSuf
from umi_log import logger


FileSuf = {  # 合法文件后缀
    "image": ImageSuf,
    "doc": DocSuf,
}


# 同步从路径中搜索后缀符合要求的文件，返回路径列表。
def findFiles(
    paths: List,  # 初始路径列表
    sufType: str,  # 后缀类型，FileSuf的key
    isRecurrence: bool,  # 若为True，则递归搜索
):
    if isinstance(paths, QJSValue):
        paths = paths.toVariant()
    if not isinstance(paths, list):
        logger.error(f"不合法的路径列表：{paths}, {type(paths)}")
        return []
    sufs = FileSuf.get(sufType, "")
    if not sufs:
        logger.error(f"不合法的后缀类型：{sufs}")
        return []

    def _sufMatching(path):
        return os.path.splitext(path)[-1].lower() in sufs

    filePaths = []
    for p in paths:
        if os.path.isfile(p) and _sufMatching(p):  # 是文件，直接判断
            filePaths.append(os.path.abspath(p))
        elif os.path.isdir(p):  # 是目录
            if isRecurrence:  # 需要递归
                for root, dirs, files in os.walk(p):
                    for file in files:
                        if _sufMatching(file):  # 收集子文件
                            filePaths.append(
                                os.path.abspath(os.path.join(root, file))
                            )  # 将路径转换为绝对路径
            else:  # 不递归读取子文件夹
                for file in os.listdir(p):
                    if os.path.isfile(os.path.join(p, file)) and _sufMatching(file):
                        filePaths.append(os.path.abspath(os.path.join(p, file)))
    for i, p in enumerate(filePaths):  # 规范化正斜杠
        filePaths[i] = p.replace("\\", "/")
    return filePaths


# 异步从路径中搜索后缀符合要求的文件，并定时刷新UI。
# image: 返回路径列表
# doc: 返回 MissionDOC.getDocInfo 的信息字典列表
def asynFindFiles(
    paths: List,  # 初始路径列表
    sufType: str,  # 后缀类型，FileSuf的key
    isRecurrence: bool,  # 若为True，则递归搜索
    completeKey: str,  # 全部完成后的事件key。向事件传入合法路径列表。
    updateKey: str,  # UI刷新进度的事件key。填""则不刷新。向事件传入 (已完成的路径数量, 最近一条路径)
    updateTime: float,  # UI刷新进度的间距
):
    if isinstance(paths, QJSValue):
        paths = paths.toVariant()
    if not isinstance(paths, list):
        logger.error(f"不合法的路径列表：{paths}, {type(paths)}")
        PubSubService.publish(completeKey, [])
        return
    sufs = FileSuf.get(sufType, "")
    if not sufs:
        logger.error(f"不合法的后缀类型：{sufs}")
        PubSubService.publish(completeKey, [])
        return

    def _sufMatching(path):
        return os.path.splitext(path)[-1].lower() in sufs

    if not updateKey:  # 如果没有刷新事件，则刷新间隔为无穷大
        updateTime = float("inf")
    filePaths = []
    lastTime = 0  # 上一次update事件的时间

    def updateEvent(fp):
        nonlocal lastTime
        now = time.time()
        if now - lastTime > updateTime:
            PubSubService.publish(updateKey, len(filePaths), fp)
            lastTime = now

    def addFile(fp):
        fp = fp.replace("\\", "/")  # 规范化正斜杠
        if sufType == "doc":  # 文档读取信息
            info = MissionDOC.getDocInfo(fp)
            if "error" in info:
                logger.warning(f'读入文档失败：{fp}, {info["error"]}')
            else:
                filePaths.append(info)
        else:
            filePaths.append(fp)
        updateEvent(fp)

    for p in paths:
        if os.path.isfile(p) and _sufMatching(p):  # 是文件，直接判断
            addFile(os.path.abspath(p))
        elif os.path.isdir(p):  # 是目录
            if isRecurrence:  # 需要递归
                for root, dirs, files in os.walk(p):
                    for file in files:
                        if _sufMatching(file):  # 收集子文件
                            # 转换为绝对路径
                            fp = os.path.abspath(os.path.join(root, file))
                            addFile(fp)
            else:  # 不递归读取子文件夹
                for file in os.listdir(p):
                    if os.path.isfile(os.path.join(p, file)) and _sufMatching(file):
                        fp = os.path.abspath(os.path.join(p, file))
                        addFile(fp)

    PubSubService.publish(completeKey, filePaths)
