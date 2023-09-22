# 处理命令行指令，向已在运行的进程发送指令

from ..utils import pre_configs
from ..platform import Platform

import sys
import time
import subprocess


def initCmd():
    # 通过 web api 检查是否已有进程在运行
    port = pre_configs.getValue("server_port")  # 记录的端口号
    usedPorts = Platform.getUsedPorts()  # 已占用的端口号
    t1 = time.time()
    if port in usedPorts:
        print(f"接口{port}已被占用，尝试探测Umi")
        import urllib.request

        try:
            url = f"http://127.0.0.1:{port}/umiocr"
            response = urllib.request.urlopen(url)
            # 检查响应状态码
            if response.status == 200:
                data = response.read().decode("utf-8")
                if data.startswith("Umi-OCR"):
                    print(data)
                    t2 = time.time()
                    print("== 已有进程在启动！！", t2 - t1)
                    return False
            else:
                print("请求失败，状态码：", response.status)
        except Exception as e:
            print("请求失败，异常：", e)

    t2 = time.time()
    print("= 探测网络耗时:", t2 - t1)
    print("== 命令行个数")
    print(len(sys.argv))
    return True
    # return False
