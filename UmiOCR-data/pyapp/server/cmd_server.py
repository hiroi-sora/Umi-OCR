# ===============================================
# =============== 命令行-解析和执行 ===============
# ===============================================

import argparse


class _Cmd:
    def __init__(self):
        self._parser = None

    def init(self):
        if self._parser:
            return
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument("--show", help="Display App", action="store_true")

    # 分析指令，返回指令对象
    def parse(self, argv):
        self.init()
        if len(argv) == 0:  # 空指令，则补充--show
            argv = ["--show"]
        print("= 命令行接收参数：", argv)
        try:
            return self._parser.parse_args(argv)
        except SystemExit as e:
            if str(e) == "0":
                return self._parser.format_help()
            return f"Your argv: {argv}\n[Error]: {e}\n\n{self._parser.format_help()}"
        except Exception as e:
            return f"Your argv: {argv}\n[Error]: {e}\n\n{self._parser.format_help()}"

    # 执行指令，返回执行结果字符串
    def execute(self, argv):
        args = self.parse(argv)
        if type(args) == str:
            return args
        print("= 命令行解析参数：", args)


CmdServer = _Cmd()
# res = CmdServer.execute(["--show"])
# print("=====================")
# print(res)
# import sys

# sys.exit(0)
