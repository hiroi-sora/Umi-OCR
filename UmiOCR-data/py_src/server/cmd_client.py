# ============================================
# =============== 命令行-客户端 ===============
# ============================================

from ..utils import pre_configs
from ..platform import Platform

from umi_about import UmiAbout  # 项目信息
import os
import sys
import time
import psutil


# 获取进程的创建时间
def getPidTime(pid):
    try:
        return str(psutil.Process(pid).create_time())
    except psutil.NoSuchProcess as e:
        # 虽然psutil.pid_exists验证pid存在，但 Process 无法生成对象
        return ""


# 检查软件多开
def _isMultiOpen():
    # 检查上次记录的pid和key是否还在运行
    recordPID = pre_configs.getValue("last_pid")
    recordPTime = pre_configs.getValue("last_ptime")
    if psutil.pid_exists(recordPID):  # 上次记录的pid如今存在
        processTime = getPidTime(recordPID)
        if recordPTime == processTime:  # 当前该进程启动时间与记录的相同，则为多开
            return True
    return False


# 输出
def _output(argv, argument, mode, text):
    if argument not in argv:
        return
    path = ""
    # 提取路径参数
    try:
        i = argv.index(argument)
        path = argv[i + 1]
        del argv[i : i + 2]
    except Exception as e:
        print(f"[Error] argument {argument} cannot be resolved. \n{e}")
        return
    # 相对路径转绝对路径
    if not os.path.isabs(path):
        # 获取当前工作目录的上一级目录
        current_dir = os.getcwd()
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        # 将 path 转为绝对路径，且以上一级目录为基准
        path = os.path.abspath(os.path.join(parent_dir, path))
    try:
        with open(path, mode, encoding="utf-8") as f:
            f.write(text)
        print(f"Success output to file: {path}")
    except Exception as e:
        print(f"[Error] failed to write file {path} : \n{e}")
        return


# 跨进程发送指令
def _sendCmd(argv):
    port = pre_configs.getValue("server_port")  # 记录的端口号
    url = f"http://127.0.0.1:{port}/argv"  # argv，指令列表接口
    errStr = f"Umi-OCR 已在运行，HTTP跨进程传输指令失败。\n[Error] Umi-OCR is already running, HTTP cross process transmission instruction failed.\n{url}"
    import urllib.request
    import json

    # 向后台工作进程发送指令
    res = ""
    try:
        data = json.dumps(argv, ensure_ascii=True).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(req)
        if response.status == 200:
            res = response.read().decode("utf-8")
        else:
            res = f"{errStr}\nstatus_code: {response.status}"
    except Exception as e:
        res = f"{errStr}\nerror: {e}"
    # 输出
    print(res)
    _output(argv, "-->", "w", res)
    _output(argv, "-->>", "a", res)


# 启动新进程，并发送指令
def _newSend(argv):
    appPath = UmiAbout["app"]["path"]
    if not appPath:
        msg = "未找到 Umi-OCR.exe 的路径，无法启动新进程。请手动启动Umi-OCR后发送指令。\nUmi-OCR.exe path not found, unable to start a new process."
        os.MessageBox(msg)
        return
    # 启动进程，传入强制参数，避免递归无限启动进程
    Platform.runNewProcess(appPath, " --force")
    # 等待并检查 服务进程初始化完毕
    for i in range(60):  # 检测轮次
        time.sleep(0.5)  # 每次等待时间
        pre_configs.readConfigs()  # 重新读取预配置
        if _isMultiOpen():  # 检测新进程是否启动
            _sendCmd(argv)  # 发送指令
            return
    print(
        "服务进程初始化失败，等待时间超时。\n[Error] The service process initialization failed and the waiting time timed out."
    )


# 初始化命令行
def initCmd():
    argv = sys.argv[1:]
    force = False
    if "--force" in argv:
        argv.remove("--force")
        force = True
    # 检查，发现软件多开，则向已在运行的进程发送初始指令
    if _isMultiOpen():
        _sendCmd(argv)
        return False
    # 未多开，则启动进程
    else:
        # 无参数或强制启动，则正常运行本进程，刷新pid和ptime
        if not argv or force:
            nowPid = os.getpid()
            nowPTime = getPidTime(nowPid)
            pre_configs.setValue("last_pid", nowPid)
            pre_configs.setValue("last_ptime", nowPTime)
            return True
        else:  # 有参数，则启动新进程并发送参数
            _newSend(argv)
            return False
