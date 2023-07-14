import utils.gflags as gflags
from utils.logger import GetLog
from utils.config import Config, WindowTopModeFlag

import re
import os
import time
import asyncio
import threading
import win32pipe  # 管道相关
import win32file
import tkinter as tk

Log = GetLog()

# ======================= 参数解析 ===================================

Flags = gflags.FLAGS
# 设置
gflags.DEFINE_integer('language', -1, '更改识别语言。传入序号(从0开始)，切换为设置页中对应序号的语言。')
gflags.DEFINE_integer('window_top_mode', -1, '窗口置顶模式。0为静默模式，1为自动弹出。')
gflags.DEFINE_string('output_file_path', '', '指定输出文件的目录（文件夹）。')
gflags.DEFINE_string('output_file_name', '', '指定输出文件的文件名（不含后缀）。')
# 指令
gflags.DEFINE_bool('hide', False, 'true时隐藏窗口，最小化到托盘。')
gflags.DEFINE_bool('show', False, 'true时将主窗口弹出到最前方。')
gflags.DEFINE_bool('exit', False, 'true时退出Umi-OCR。')
# 任务
gflags.DEFINE_bool('clipboard', False, 'true时读取一次剪贴板进行识图。')
gflags.DEFINE_bool('screenshot', False, 'true时进行一次截屏识图。')
gflags.DEFINE_string('img', '', '传入本地图片路径。含空格的路径用引号""括起来。多个路径可用逗号,连接。')


DictDefault = Flags.FlagValuesDict()  # 生成默认值字典


def Parse(args):  # 解析参数。传入参数列表，返回解析后的字典。
    try:
        Flags.Reset()  # 清空旧参数
        Flags(args)  # 解析参数
        f = Flags.FlagValuesDict()  # 转字典
        if f['img']:  # 处理图片地址
            if ',' in f['img']:  # 多个地址切割
                f['img'] = f['img'].split(',')
            else:  # 单个地址包装
                f['img'] = [f['img']]
        return f
    except Exception as e:
        return {'error': f'命令行参数解析异常。\n参数：{args}\n错误：{e}', **DictDefault}


def Mission(flags):
    '''执行任务。传入参数字典'''

    # 设置&指令
    if flags['exit']:  # 退出
        Config.main.win.event_generate('<<QuitEvent>>')
        return
    if flags['show']:  # 显示主窗
        Config.main.gotoTop(isForce=True)
    elif flags['hide']:  # 隐藏主窗
        # 若有托盘且启用了最小化到托盘
        if Config.get('isTray') and Config.get('isBackground'):
            Config.main.onCloseWin()  # 关闭窗口
        else:  # 若没有，则
            Config.main.win.iconify()  # 最小化
    if flags['language'] > -1:  # 切换语言
        lans, index = list(Config.get("ocrConfig").keys()), flags['language']
        if(index < len(lans)):
            Config.set("ocrConfigName", lans[index])
    if flags['window_top_mode'] == 0:  # 窗口弹出模式
        Config.set("WindowTopMode", WindowTopModeFlag.never)
    elif flags['window_top_mode'] == 1:
        Config.set("WindowTopMode", WindowTopModeFlag.finish)
    if flags['output_file_path']:  # 输出文件目录
        Config.set("outputFilePath", flags['output_file_path'])
    if flags['output_file_name']:  # 输出文件文件名前缀
        Config.set("outputFileName", flags['output_file_name'])

    # 任务
    if not Config.main.isMsnReady():
        tk.messagebox.showerror(
            '遇到了一点小问题', '当前已有任务进行。')
        return
    if flags['img']:
        Config.main.clearTable()  # 清空表格
        Config.main.addImagesList(flags['img'])  # 导入路径
        Config.main.run()  # 开始运行
    elif flags['clipboard']:
        Config.main.runClipboard()
    elif flags['screenshot']:
        Config.main.openScreenshot()


def ParseStr(strin):  # 解析参数。传入参数字符串，直接执行。
    # 匹配所有双引号内的内容
    pattern = r'"[^"]*"'
    matches = re.findall(pattern, strin)
    # 将匹配到的内容替换为特殊标记
    for i, match in enumerate(matches):
        strin = strin.replace(match, f'__QUOTE_MARK_{i}__')
    # 按照空格进行分割
    result = strin.split()
    # 将特殊标记替换回双引号内的内容
    for i, match in enumerate(matches):
        result = [
            x.replace(f'__QUOTE_MARK_{i}__', match[1:-1]) for x in result]
    args = ['', *result]  # 第一位为空
    flags = Parse(args)
    if 'error' in flags:
        tk.messagebox.showerror(
            '遇到了一点小问题', flags['error'])
        return
    Mission(flags)

# ======================= 监听指令 ===================================


pipeName = r'\\.\pipe\umiocr'  # 命名管道
pipeBufferSize = 65535  # 管道缓冲区大小


class Listener:

    def __init__(self):
        # 启动外部命令监听线程
        def runLoop():  # 启动事件循环
            asyncio.set_event_loop(self.__runMissionLoop)
            self.__runMissionLoop.run_forever()

        # 在当前线程下创建事件循环
        self.__runMissionLoop = asyncio.new_event_loop()
        # 开启新的线程，在新线程中启动事件循环
        threading.Thread(target=runLoop).start()
        # 在新线程中事件循环不断游走执行
        asyncio.run_coroutine_threadsafe(
            self.__listener(), self.__runMissionLoop)

    async def __listener(self):  # 监听器
        # 检查命名管道是否已存在
        if os.path.exists(pipeName):
            Log.error(f'命名管道{pipeName}已存在！')
            return
        # 设置命名管道
        pipe = win32pipe.CreateNamedPipe(
            pipeName,  # 管道名称
            win32pipe.PIPE_ACCESS_DUPLEX,  # 打开模式：可读可写
            # 管道模式：报文、等待时挂起线程
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,  # 最大实例数，无限制
            pipeBufferSize,  # 输出缓冲区大小
            pipeBufferSize,  # 输入缓冲区大小
            0,  # 默认超时时间
            None  # 安全属性
        )

        # 等待程序初始化完成
        while not Config.isInit():
            time.sleep(0.1)

        while True:
            try:
                # 连接命名管道
                Log.info(f"命名管道{pipeName}等待连接")
                win32pipe.ConnectNamedPipe(pipe, None)

                # 循环监听管道传来的消息
                while True:
                    try:
                        # 读取命名管道数据
                        indata = win32file.ReadFile(
                            pipe, pipeBufferSize)
                        print(f"==============读取数据：\n{indata}")
                        data = indata[1].decode()
                        ParseStr(data)  # 分析并执行
                    except Exception as e:
                        print(f"读取数据出错：{e}")
                        break
            finally:  # 某个客户端断开连接
                try:
                    win32pipe.DisconnectNamedPipe(pipe)  # 关闭管道，下一次重开
                except:
                    pass


Listener()  # 启动监听

# echo hello > \\.\pipe\umiocr
