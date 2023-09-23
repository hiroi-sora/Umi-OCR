# ============================================
# =============== 命令行-客户端 ===============
# ============================================

from ..utils import pre_configs
from ..platform import Platform

import os
import sys
import psutil


# 检查软件多开
def _isMultiOpen():
    def getPidTime(pid):  # 获取进程的创建时间
        try:
            return str(psutil.Process(pid).create_time())
        except psutil.NoSuchProcess as e:  # 虽然psutil.pid_exists验证pid存在，但 Process 无法生成对象
            return ""

    # 检查上次记录的pid和key是否还在运行
    recordPID = pre_configs.getValue("last_pid")
    recordPTime = pre_configs.getValue("last_ptime")
    if psutil.pid_exists(recordPID):  # 上次记录的pid如今存在
        processTime = getPidTime(recordPID)
        if recordPTime == processTime:  # 当前该进程启动时间与记录的相同，则为多开
            return True
    # 未多开，则刷新pid和ptime
    nowPid = os.getpid()
    nowPTime = getPidTime(nowPid)
    pre_configs.setValue("last_pid", nowPid)
    pre_configs.setValue("last_ptime", nowPTime)
    return False


# 跨进程发送指令
def _sendCmd():
    argv = sys.argv[1:]  # 获取要发送的指令
    port = pre_configs.getValue("server_port")  # 记录的端口号
    url = f"http://127.0.0.1:{port}/argv"  # argv，指令列表接口
    errStr = f"Umi-OCR 已在运行，HTTP跨进程传输指令失败。\nUmi-OCR is already running, HTTP cross process transmission instruction failed.\n{url}"
    import urllib.request
    import json

    try:
        data = json.dumps(argv, ensure_ascii=True).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(req)
        if response.status == 200:
            data = response.read().decode("utf-8")
            print(data)
        else:
            print(f"{errStr}\nstatus_code: {response.status}")
    except Exception as e:
        print(f"{errStr}\nerror: {e}")


# 初始化命令行
def initCmd():
    # 检查，发现软件多开，则向已在运行的进程发送初始指令
    if _isMultiOpen():
        _sendCmd()
        return False
    # 未多开，则正常启动
    else:
        argv = sys.argv[1:]
        return True
