# 调用 RapidOCR-json.exe 的 Python Api
# 项目主页：
# https://github.com/hiroi-sora/RapidOCR-json

from .api_ocr import ApiOcr
from ...utils.call_func import CallFunc

import os
import psutil  # 进程检查
import atexit  # 退出处理
import subprocess  # 进程，管道
from json import loads as jsonLoads, dumps as jsonDumps
from sys import platform as sysPlatform  # popen静默模式
from base64 import b64encode  # base64 编码


class Rapid_pipe:  # 调用OCR（管道模式）
    def __init__(self, exePath: str, argument: dict = None):
        """初始化识别器（管道模式）。\n
        `exePath`: 识别器`PaddleOCR_json.exe`的路径。\n
        `argument`: 启动参数，字典`{"键":值}`。参数说明见 https://github.com/hiroi-sora/PaddleOCR-json
        """
        cwd = os.path.abspath(os.path.join(exePath, os.pardir))  # 获取exe父文件夹
        # 处理启动参数
        if not argument == None:
            for key, value in argument.items():
                if isinstance(value, str):  # 字符串类型的值加双引号
                    exePath += f' --{key}="{value}"'
                else:
                    exePath += f" --{key}={value}"
        if "ensureAscii" not in exePath:
            exePath += f" --ensureAscii=1"
        # 设置子进程启用静默模式，不显示控制台窗口
        self.ret = None
        startupinfo = None
        if "win32" in str(sysPlatform).lower():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = (
                subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            )
            startupinfo.wShowWindow = subprocess.SW_HIDE
        self.ret = subprocess.Popen(  # 打开管道
            exePath,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # 丢弃stderr的内容
            startupinfo=startupinfo,  # 开启静默模式
        )
        # 启动子进程
        while True:
            if not self.ret.poll() == None:  # 子进程已退出，初始化失败
                raise Exception(f"OCR init fail.")
            initStr = self.ret.stdout.readline().decode("utf-8", errors="ignore")
            if "OCR init completed." in initStr:  # 初始化成功
                break
        atexit.register(self.exit)  # 注册程序终止时执行强制停止子进程

    def runDict(self, writeDict: dict):
        """传入指令字典，发送给引擎进程。\n
        `writeDict`: 指令字典。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        # 检查子进程
        if not self.ret:
            return {"code": 901, "data": f"引擎实例不存在。"}
        if not self.ret.poll() == None:
            return {"code": 902, "data": f"子进程已崩溃。"}
        # 输入信息
        writeStr = jsonDumps(writeDict, ensure_ascii=True, indent=None) + "\n"
        try:
            self.ret.stdin.write(writeStr.encode("utf-8"))
            self.ret.stdin.flush()
        except Exception as e:
            return {"code": 902, "data": f"向识别器进程传入指令失败，疑似子进程已崩溃。{e}"}
        # 获取返回值
        try:
            getStr = self.ret.stdout.readline().decode("utf-8", errors="ignore")
        except Exception as e:
            return {"code": 903, "data": f"读取识别器进程输出值失败。异常信息：[{e}]"}
        try:
            return jsonLoads(getStr)
        except Exception as e:
            return {"code": 904, "data": f"识别器输出值反序列化JSON失败。异常信息：[{e}]。原始内容：[{getStr}]"}

    def run(self, imgPath: str):
        """对一张本地图片进行文字识别。\n
        `exePath`: 图片路径。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        writeDict = {"image_path": imgPath}
        return self.runDict(writeDict)

    def runBase64(self, imageBase64: str):
        """对一张编码为base64字符串的图片进行文字识别。\n
        `imageBase64`: 图片base64字符串。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        writeDict = {"image_base64": imageBase64}
        return self.runDict(writeDict)

    def runBytes(self, imageBytes):
        """对一张图片的字节流信息进行文字识别。\n
        `imageBytes`: 图片字节流。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        imageBase64 = b64encode(imageBytes).decode("utf-8")
        return self.runBase64(imageBase64)

    def exit(self):
        """关闭引擎子进程"""
        if not self.ret:
            return
        self.ret.kill()  # 关闭子进程
        self.ret = None
        atexit.unregister(self.exit)  # 移除退出处理
        print("### RapidOCR引擎子进程关闭！")

    @staticmethod
    def printResult(res: dict):
        """用于调试，格式化打印识别结果。\n
        `res`: OCR识别结果。"""

        # 识别成功
        if res["code"] == 100:
            index = 1
            for line in res["data"]:
                print(f"{index}-置信度：{round(line['score'], 2)}，文本：{line['text']}")
                index += 1
        elif res["code"] == 100:
            print("图片中未识别出文字。")
        else:
            print(f"图片识别失败。错误码：{res['code']}，错误信息：{res['data']}")

    def __del__(self):
        self.exit()


# 配置映射表，表1为全局，2为局部。每一项为： ["exe键", "qml键"]
ConfigMap1 = [
    ("exe_path", "ocr.RapidOCR.path"),  # 引擎路径
]
ConfigMap2 = [
    ("language", "ocr.language"),  # 配置文件路径
    ("cls", "ocr.cls"),  # 方向分类
    ("use_angle_cls", "ocr.cls"),  # 方向分类
    ("limit_side_len", "ocr.limit_side_len"),  # 长边压缩
]


class ApiRapidOcr(ApiOcr):  # 公开接口
    def __init__(self, globalArgd):
        # 测试路径是否存在
        self.exePath = globalArgd["ocr.RapidOCR.path"]
        if not os.path.exists(self.exePath):
            raise ValueError(f'[Error] Exe path "{self.exePath}" does not exist.')
        # 初始化参数
        self.api = None  # api对象
        self.argd = None  # 最终参数字典
        self.langDict = {}  # 语言字典

    def start(self, argd):  # 启动引擎。返回： "" 成功，"[Error] xxx" 失败
        a = {"models": "models"}  # 加载局部参数
        if argd["ocr.language"] in self.langDict:
            lang = self.langDict[argd["ocr.language"]]
            a.update(
                {
                    "det": lang["det"],
                    "cls": lang["cls"],
                    "rec": lang["rec"],
                    "keys": lang["keys"],
                }
            )
        else:
            return f'[Error] language {argd["language"]} not in langDict.'
        if argd["ocr.angle"]:
            a.update({"doAngle": 1, "mostAngle": 1})
        else:
            a.update({"doAngle": 1, "mostAngle": 1})
        self.argd = a.copy()
        # 启动引擎
        try:
            self.api = Rapid_pipe(self.exePath, a)
        except Exception as e:
            self.api = None
            return f"[Error] OCR init fail. Argd: {a}"
        return ""

    def stop(self):  # 停止引擎
        if self.api == None:
            return
        self.api.exit()
        self.api = None

    def restart(self):  # 重启引擎
        self.stop()
        a = self.argd.copy()
        # 启动引擎
        try:
            self.api = Rapid_pipe(self.exePath, a)
            print("重启引擎")
        except Exception as e:
            self.api = None
            print(f"[Error]重启引擎失败: {e}")

    def runPath(self, imgPath: str):  # 路径识图
        res = self.api.run(imgPath)
        return res

    def runBytes(self, imageBytes):  # 字节流
        res = self.api.runBytes(imageBytes)
        return res

    def getApiInfo(self):  # 获取额外信息
        # 动态载入模型库
        optionsList = []
        configsPath = os.path.dirname(self.exePath) + "/models/configs.txt"
        try:
            with open(configsPath, "r", encoding="utf-8") as file:
                content = file.read()
                parts = content.split("\n\n")
                for part in parts:
                    items = part.split("\n")
                    if len(items) == 5:
                        title, det, cls, rec, keys = items
                        self.langDict[title] = {
                            "det": det,
                            "cls": cls,
                            "rec": rec,
                            "keys": keys,
                        }
                        optionsList.append([title, title])
        except FileNotFoundError:
            print("【Error】RapidOCR配置文件configs不存在，请检查文件路径是否正确。", configsPath)
        except IOError:
            print("【Error】RapidOCR配置文件configs无法打开或读取。")

        return {"language": {"optionsList": optionsList}}
