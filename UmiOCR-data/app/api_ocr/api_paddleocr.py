# 调用 PaddleOCR-json.exe 的 Python Api
# 项目主页：
# https://github.com/hiroi-sora/PaddleOCR-json

from .api_ocr import ApiOcr

import os
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


class ApiPaddleOcr(ApiOcr):  # 公开接口
    def __init__(self):
        self.api = None
        self.args = {}

    def start(self, argd):  # 启动引擎
        if not self.api == None:
            # 若引擎已启动，且参数与传入参数一致，则无需重启
            if not set(argd.items()) == set(self.args.items()):
                return
            # 若引擎已启动但需要更改参数，则停止旧引擎
            self.stop()
        # 启动新引擎
        self.args = argd
        exePath = argd["exePath"]
        del argd["exePath"]
        self.api = PPOCR_pipe(exePath, argd)

    def stop(self):  # 停止引擎
        if self.api == None:
            return
        self.api.exit()
        self.api = None

    def runPath(self, imgPath: str):  # 路径识图
        return self.api.run(imgPath)

    def runClipboard(self):  # 剪贴板识图
        return self.api.runClipboard()

    def runBytes(self, imageBytes):  # 字节流
        return self.api.runBytes(imageBytes)
