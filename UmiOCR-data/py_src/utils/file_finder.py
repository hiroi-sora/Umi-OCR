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
from umi_log import logger


FileSuf = {  # 合法文件后缀
    "image": [
        ".jpg",
        ".jpe",
        ".jpeg",
        ".jfif",
        ".png",
        ".webp",
        ".bmp",
        ".tif",
        ".tiff",
    ],
    "doc": [
        ".pdf",
        ".xps",
        ".epub",
        ".mobi",
        ".fb2",
        ".cbz",
    ],
}


# 异步从路径中搜索后缀符合要求的文件
def asynFindFiles(
    paths: List,  # 初始路径列表
    sufType: str,  # 后缀类型，FileSuf的key
    isRecurrence: bool,  # 若为True，则递归搜索
    completeKey: str,  # 全部完成后的事件key。向事件传入合法路径列表。
    updateKey: str = "",  # 加载中刷新进度的key，不填则无。向事件传入 (已完成的路径数量, 最近一条路径)
    updateTime: float = 1.0,  # 刷新进度的间距
):
    print("开始！！！")
    sufs = FileSuf.get(sufType, "")
    if not sufs:
        print("不合法的后缀！！")

    def _sufMatching(path):
        return os.path.splitext(path)[-1].lower() in sufs

    if isinstance(paths, QJSValue):
        paths = paths.toVariant()
    if not isinstance(paths, list):
        logger.error(f"_findFiles 传入：{paths}, {type(paths)}")
        return []
    if not updateKey:  # 如果没有刷新事件，则刷新间隔为无穷大
        updateTime = float("inf")
    updateTime
    filePaths = []
    lastTime = time.time()  # 上一次update事件的时间

    def updateEvent(fp):
        nonlocal lastTime
        if time.time() - lastTime > updateTime:
            PubSubService.publish(updateKey, len(filePaths), fp)

    for p in paths:
        if os.path.isfile(p) and _sufMatching(p):  # 是文件，直接判断
            filePaths.append(os.path.abspath(p))
        elif os.path.isdir(p):  # 是目录
            if isRecurrence:  # 需要递归
                for root, dirs, files in os.walk(p):
                    for file in files:
                        if _sufMatching(file):  # 收集子文件
                            # 转换为绝对路径
                            fp = os.path.abspath(os.path.join(root, file))
                            fp = fp.replace("\\", "/")  # 规范化正斜杠
                            filePaths.append(fp)
                            updateEvent(fp)
            else:  # 不递归读取子文件夹
                for file in os.listdir(p):
                    if os.path.isfile(os.path.join(p, file)) and _sufMatching(file):
                        fp = os.path.abspath(os.path.join(p, file))
                        fp = fp.replace("\\", "/")  # 规范化正斜杠
                        filePaths.append(fp)
                        updateEvent(fp)
                        time.sleep(0.1)

    PubSubService.publish(completeKey, filePaths)
