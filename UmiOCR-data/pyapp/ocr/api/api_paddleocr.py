# 调用 PaddleOCR-json.exe 的 Python Api
# 项目主页：
# https://github.com/hiroi-sora/PaddleOCR-json

from .api_ocr import ApiOcr
from ...utils.call_func import CallFunc

import os
import psutil  # 进程检查
import socket  # 套接字
import subprocess  # 进程，管道
from json import loads as jsonLoads, dumps as jsonDumps
from sys import platform as sysPlatform  # popen静默模式
from base64 import b64encode  # base64 编码


class PPOCR_pipe:  # 调用OCR（管道模式）
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
        # 设置子进程启用静默模式，不显示控制台窗口
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

    def runDict(self, writeDict: dict):
        """传入指令字典，发送给引擎进程。\n
        `writeDict`: 指令字典。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        # 检查子进程
        if not self.ret.poll() == None:
            return {"code": 901, "data": f"子进程已崩溃。"}
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

    def runClipboard(self):
        """立刻对剪贴板第一位的图片进行文字识别。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        return self.run("clipboard")

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
        self.ret.kill()  # 关闭子进程

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


class __PPOCR_socket(PPOCR_pipe):  # 调用OCR（套接字模式）
    def __init__(self, exePath: str, argument: dict = None):
        """初始化识别器（套接字模式）。\n
        `exePath`: 识别器`PaddleOCR_json.exe`的路径。\n
        `argument`: 启动参数，字典`{"键":值}`。参数说明见 https://github.com/hiroi-sora/PaddleOCR-json
        """
        # 处理参数
        if not argument:
            argument = {}
        argument["port"] = 0  # 随机端口号
        argument["addr"] = "loopback"  # 本地环回地址
        super().__init__(exePath, argument)  # 父类构造函数
        # 再获取一行输出，检查是否成功启动服务器
        initStr = self.ret.stdout.readline().decode("utf-8", errors="ignore")
        if not self.ret.poll() == None:  # 子进程已退出，初始化失败
            raise Exception(f"Socket init fail.")
        if "Socket init completed. " in initStr:  # 初始化成功
            splits = initStr.split(":")
            self.ip = splits[0].split("Socket init completed. ")[1]
            self.port = int(splits[1])  # 提取端口号
            self.ret.stdout.close()  # 关闭管道重定向，防止缓冲区填满导致堵塞
            print(f"套接字服务器初始化成功。{self.ip}:{self.port}")
            return
        # 异常
        self.exit()
        raise Exception(f"Socket init fail.")

    def runDict(self, writeDict: dict):
        """传入指令字典，发送给引擎进程。\n
        `writeDict`: 指令字典。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        # 检查子进程
        if not self.ret.poll() == None:
            return {"code": 901, "data": f"子进程已崩溃。"}
        # 通信
        writeStr = jsonDumps(writeDict, ensure_ascii=True, indent=None) + "\n"
        try:
            # 创建TCP连接
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((self.ip, self.port))
            # 发送数据
            clientSocket.sendall(writeStr.encode())
            # 接收数据
            resData = b""
            while True:
                chunk = clientSocket.recv(1024)
                if not chunk:
                    break
                resData += chunk
            getStr = resData.decode()
        except ConnectionRefusedError:
            return {"code": 902, "data": "连接被拒绝"}
        except TimeoutError:
            return {"code": 903, "data": "连接超时"}
        except Exception as e:
            return {"code": 904, "data": f"网络错误：{e}"}
        finally:
            clientSocket.close()  # 关闭连接
        # 反序列输出信息
        try:
            return jsonLoads(getStr)
        except Exception as e:
            return {"code": 905, "data": f"识别器输出值反序列化JSON失败。异常信息：[{e}]。原始内容：[{getStr}]"}


# 配置映射表，表1为全局，2为局部。每一项为： ["exe键", "qml键"]
ConfigMap1 = [
    ("exe_path", "ocr.PaddleOCR.path"),  # 引擎路径
    ("enable_mkldnn", "ocr.PaddleOCR.enable_mkldnn"),  # mkl加速
]
ConfigMap2 = [
    ("config_path", "ocr.language"),  # 配置文件路径
    ("cls", "ocr.cls"),  # 方向分类
    ("use_angle_cls", "ocr.cls"),  # 方向分类
    ("limit_side_len", "ocr.limit_side_len"),  # 长边压缩
]


class ApiPaddleOcr(ApiOcr):  # 公开接口
    def __init__(self, globalArgd):
        # 测试路径是否存在
        pathKey = ConfigMap1[0][1]
        if pathKey not in globalArgd:
            raise ValueError(f'[Error] Missing parameter "{pathKey}".')
        if not os.path.exists(globalArgd[pathKey]):
            raise ValueError(
                f'[Error] Exe path "{globalArgd[pathKey]}" does not exist.'
            )
        # 初始化参数
        self.api = None  # api对象
        self.lArgs = None  # 局部参数
        self.gArgd = {}  # 全局参数
        self.argd = None  # 最终参数字典
        for c in ConfigMap1:  # 加载全局参数
            if c[1] not in globalArgd:
                raise ValueError(f'[Error] global Key "{c[1]}" not in qml config dict.')
            self.gArgd[c[0]] = globalArgd[c[1]]
        # 内存清理参数
        self.ramInfo = {"max": -1, "time": -1, "timerID": ""}
        if "ocr.PaddleOCR.ram_max" in globalArgd:
            m = globalArgd["ocr.PaddleOCR.ram_max"]
            if isinstance(m, (int, float)):
                self.ramInfo["max"] = m
        if "ocr.PaddleOCR.ram_time" in globalArgd:
            m = globalArgd["ocr.PaddleOCR.ram_time"]
            if isinstance(m, (int, float)):
                self.ramInfo["time"] = m

    def start(self, argd):  # 启动引擎。返回： "" 成功，"[Error] xxx" 失败
        # 加载局部参数
        lArgd = {}
        for c in ConfigMap2:
            if c[1] not in argd:
                return f'[Error] Local key "{c[1]}" not in qml config dict.'
            lArgd[c[0]] = argd[c[1]]
        if not self.api == None:
            # 若引擎已启动，且局部参数与传入参数一致，则无需重启
            if set(lArgd.items()) == self.lArgs:
                return ""
            # 若引擎已启动但需要更改参数，则停止旧引擎
            self.stop()
        # 启动新引擎
        self.lArgs = set(lArgd.items())  # 记录局部参数
        # 拼合最终参数
        lArgd.update(self.gArgd)
        self.argd = lArgd.copy()
        exePath = lArgd["exe_path"]
        del lArgd["exe_path"]
        # 启动引擎
        try:
            self.api = PPOCR_pipe(exePath, lArgd)
        except Exception as e:
            self.api = None
            return f"[Error] OCR init fail. Argd: {lArgd}"
        return ""

    def stop(self):  # 停止引擎
        if self.api == None:
            return
        self.api.exit()
        self.api = None

    def restart(self):  # 重启引擎
        self.stop()
        lArgd = self.argd.copy()
        exePath = lArgd["exe_path"]
        del lArgd["exe_path"]
        # 启动引擎
        try:
            self.api = PPOCR_pipe(exePath, lArgd)
            print("重启引擎")
        except Exception as e:
            self.api = None
            print(f"[Error]重启引擎失败: {e}")

    def runPath(self, imgPath: str):  # 路径识图
        self.__runBefore()
        res = self.api.run(imgPath)
        self.__ramClear()
        return res

    def runClipboard(self):  # 剪贴板识图
        self.__runBefore()
        res = self.api.runClipboard()
        self.__ramClear()
        return res

    def runBytes(self, imageBytes):  # 字节流
        self.__runBefore()
        res = self.api.runBytes(imageBytes)
        self.__ramClear()
        return res

    def __runBefore(self):
        CallFunc.delayStop(self.ramInfo["timerID"])  # 停止ram清理计时器

    def __ramClear(self):  # 内存清理
        if self.ramInfo["max"] > 0:
            pid = self.api.ret.pid
            rss = psutil.Process(pid).memory_info().rss
            rss /= 1048576
            if rss > self.ramInfo["max"]:
                self.restart()
        if self.ramInfo["time"] > 0:
            self.ramInfo["timerID"] = CallFunc.delay(self.restart, self.ramInfo["time"])

    def getApiInfo(self):  # 获取额外信息
        # 动态载入模型库
        """configs.txt 格式示例：
        config_chinese.txt 简体中文
        config_en.txt English
        """
        optionsList = []
        configsPath = os.path.dirname(self.gArgd["exe_path"]) + "/models/configs.txt"
        try:
            with open(configsPath, "r", encoding="utf-8") as file:
                content = file.read()
                lines = content.split("\n")
                for l in lines:
                    parts = l.split(" ", 1)
                    optionsList.append([f"models/{parts[0]}", parts[1]])
        except FileNotFoundError:
            print("【Error】PPOCR配置文件configs不存在，请检查文件路径是否正确。", configsPath)
        except IOError:
            print("【Error】PPOCR配置文件configs无法打开或读取。")

        return {"language": {"optionsList": optionsList}}
