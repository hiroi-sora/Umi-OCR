# ===============================================
# =============== 命令行-解析和执行 ===============
# ===============================================

import argparse


# 命令执行器
class _Actuator:
    def __init__(self):
        self.pyDict = {}  # python模块字典
        self.qmlDict = {}  # qml模块字典
        self.tagPageConn = None  # 页面连接器的引用

    # 初始化，并收集信息。传入qml模块字典
    def initCollect(self, qmlModuleDict):
        qmlModuleDict = qmlModuleDict.toVariant()
        self.qmlDict.update(qmlModuleDict)
        # 获取页面连接器实例
        from ..tag_pages.tag_pages_connector import TagPageConnObj

        self.tagPageConn = TagPageConnObj

        print(self.getModulesHelp())
        print(self.getModuleFuncsHelp("ScreenshotOCR", "py"))

    # 返回所有可调用模块
    def getModules(self):
        pyd, qmld = {}, {}
        pages = self.tagPageConn.pages
        for p in pages:
            if pages[p]["qmlObj"]:
                qmld[p] = pages[p]["qmlObj"]
            if pages[p]["pyObj"]:
                pyd[p] = pages[p]["pyObj"]
        pyd.update(self.pyDict)
        qmld.update(self.qmlDict)
        return {"py": pyd, "qml": qmld}

    # 传入模块名，搜索并返回模块实例。type: py / qml
    def getModuleFromName(self, moduleName, type_):
        d = self.getModules()[type_]
        module = None
        if moduleName in d:
            module = d[moduleName]
        else:
            for name in d.keys():  # 若输入模块名的前几个字母，也可以匹配
                if name.startswith(moduleName):
                    module = d[name]
                    break
        return module

    # 返回所有可调用模块的帮助信息
    def getModulesHelp(self):
        modules = self.getModules()
        help = f'Python modules: \n    {", ".join(modules["py"].keys())}\n\n'
        help += f'Qml modules: \n    {", ".join(modules["qml"].keys())}'
        return help

    # 返回一个模块的函数的帮助信息
    def getModuleFuncsHelp(self, moduleName, type_):
        module = self.getModuleFromName(moduleName, type_)
        typeStr = "Python" if type_ == "py" else "qml"
        if not module:
            return f'[Error] {typeStr} module "{moduleName}" non-existent.'
        funcs = [
            func
            for func in vars(type(module)).keys()
            if callable(getattr(module, func))
        ]
        help = f'All methods in {typeStr} module "{moduleName}":\n'
        print("=======================")
        for f in funcs:
            f = str(f)
            if not f.startswith("_"):
                help += f + "\n"
        return help

    # 调用一个模块函数。type: py / qml
    def call(self, moduleName, type_, funcName, *paras):
        module = self.getModuleFromName(type_)
        typeStr = "Python" if type_ == "py" else "qml"
        if not module:
            return f'[Error] {typeStr} module "{moduleName}" non-existent.'
        func = getattr(module, funcName, None)
        if not func:
            return f'[Error] func "{funcName}" not exist in {typeStr} module "{moduleName}".'
        try:
            res = func(*paras)
            return str(res)
        except Exception as e:
            return f'[Error] calling {typeStr} module "{moduleName}" - "{funcName}" {paras}: {e}'


CmdActuator = _Actuator()


# 命令解析器
class _Cmd:
    def __init__(self):
        self._parser = None

    def init(self):
        if self._parser:
            return
        self._parser = argparse.ArgumentParser(prog="Umi-OCR")
        self._parser.add_argument(
            "--show", action="store_true", help="Make the app appear in the foreground."
        )
        # 函数调用
        self._parser.add_argument(
            "--all_modules",
            action="store_true",
            help="Query all module names that can be called.",
        )
        self._parser.add_argument(
            "--call_py", help="Calling a function on a Python module."
        )
        self._parser.add_argument(
            "--call_qml", help="Calling a function on a Qml module."
        )
        self._parser.add_argument("--func", help="Tab page id.")
        self._parser.add_argument("paras", nargs="*", help="parameters of [--func].")

    # 分析指令，返回指令对象或报错字符串
    def parse(self, argv):
        self.init()
        # 特殊情况
        if "-h" in argv or "--help" in argv:  # 帮助
            return self._parser.format_help()
        if len(argv) == 0:  # 空指令
            pass  # TODO
            return self._parser.format_help()
        print("= 命令行接收参数：", argv)
        # 正常解析
        try:
            return self._parser.parse_args(argv)
        except SystemExit as e:
            return f"Your argv: {argv}\n[Error]: {e}\nusage: Umi-OCR --help"
        except Exception as e:
            return f"Your argv: {argv}\n[Error]: {e}\nusage: Umi-OCR --help"

    # 执行指令，返回执行结果字符串
    def execute(self, argv):
        args = self.parse(argv)
        if type(args) == str:
            return args
        if args.all_modules:
            return CmdActuator.getModulesHelp()
        print("= 命令行解析参数：", args)


CmdServer = _Cmd()

# res = CmdServer.execute([])
# print("=====================")
# print(res)
# import sys

# sys.exit(0)
