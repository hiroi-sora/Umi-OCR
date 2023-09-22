# 处理命令行指令，向已在运行的进程发送指令

import sys


def initCmd():
    print("== 命令行个数")
    print(len(sys.argv))
    return True
    # return False
