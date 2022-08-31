# 调用 PaddleOCR-json.exe 的 Python Api
# 项目主页：
# https://github.com/hiroi-sora/PaddleOCR-json


import os
import subprocess  # 进程，管道
from sys import platform as sysPlatform  # popen静默模式
from json import loads as jsonLoads


class CallingOCR:
    """调用OCR"""

    def __init__(self, exePath, configPath="", argsStr=""):
        """初始化识别器。\n
        :exePath: 识别器`PaddleOCR_json.exe`的路径。\n
        :configPath: 配置文件`PaddleOCR_json_config_XXXX.txt`的路径。\n
        :argument: 启动参数，字符串。参数说明见\n
        `https://github.com/hiroi-sora/PaddleOCR-json#5-%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF%E8%AF%B4%E6%98%8E`\n
        """
        cwd = os.path.abspath(os.path.join(exePath, os.pardir))  # 获取exe父文件夹
        # 处理启动参数
        if argsStr:  # 添加用户指定的启动参数
            exePath += f' {argsStr}'
        if configPath and 'config_path' not in exePath:  # 指定配置参数
            exePath += f' --config_path="{configPath}"'
        if 'use_system_pause' not in exePath:  # 强制禁用暂停
            exePath += ' --use_system_pause=0'
        # 设置子进程启用静默模式，不显示控制台窗口
        startupinfo = None
        if 'win32' in str(sysPlatform).lower():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        self.ret = subprocess.Popen(  # 打开管道
            exePath, cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            startupinfo=startupinfo  # 开启静默模式
        )
        # 启动子进程
        while True:
            if not self.ret.poll() == None:  # 子进程已退出，初始化失败
                print('OCR init fail!!!!!!!!!')
                raise Exception('OCR init fail.')
            initStr = self.ret.stdout.readline().decode('gbk', errors='ignore')
            if 'OCR init completed.' in initStr:  # 初始化成功
                break
        # print(f'初始化OCR成功，进程号为{self.ret.pid}')

    def run(self, imgPath):
        """对一张图片文字识别。\n
        :exePath: 图片路径。\n
        :return:  {'code': 识别码, 'data': 内容列表或错误信息字符串}\n"""
        if not self.ret.poll() == None:
            return {'code': 400, 'data': f'子进程已崩溃。'}
        wirteStr = imgPath if imgPath[-1] == '\n' else imgPath + '\n'
        # 输入路径
        try:
            self.ret.stdin.write(wirteStr.encode('gbk'))
            self.ret.stdin.flush()
        except Exception as e:
            return {'code': 400, 'data': f'向识别器进程写入图片地址失败，疑似子进程已崩溃。{e}'}
        if imgPath[-1] == '\n':
            imgPath = imgPath[:-1]
        # 获取返回值
        try:
            getStr = self.ret.stdout.readline().decode('utf-8', errors='ignore')
        except Exception as e:
            return {'code': 401, 'data': f'读取识别器进程输出值失败，疑似传入了不存在或无法识别的图片 \"{imgPath}\" 。{e}'}
        try:
            return jsonLoads(getStr)
        except Exception as e:
            return {'code': 402, 'data': f'识别器输出值反序列化JSON失败，疑似传入了不存在或无法识别的图片 \"{imgPath}\" 。异常信息：{e}。原始内容：{getStr}'}

    def __del__(self):
        self.ret.kill()  # 关闭子进程
        # print("关闭OCR！")
