# 单次快捷任务 任务处理器

from utils.config import Config
from ocr.engine import MsnFlag
from ocr.msn import Msn
from ocr.output_panel import OutputPanel  # 输出器
from ocr.tbpu.ignore_area import TbpuIgnoreArea

import tkinter as tk
import time
from pyperclip import copy as pyperclipCopy

from utils.logger import GetLog
Log = GetLog()


class MsnQuick(Msn):

    # __init__ 在主线程内初始化，其余方法在子线程内被调用
    def __init__(self):
        # 获取接口
        self.progressbar = Config.main.progressbar  # 进度条组件
        self.setRunning = Config.main.setRunning  # 设置运行状态接口
        self.outputPanel = OutputPanel()  # 输出到面板
        # 初始化文块处理器
        self.procList = []
        tbpuClass = Config.get('tbpu').get(
            Config.get('tbpuName'), None)
        if tbpuClass:
            self.procList.append(tbpuClass())
        Log.info(f'快捷文本处理器初始化完毕！')

    def onStart(self, num):
        # 重置进度提示
        self.setRunning(MsnFlag.running)  # 先设running，再设进度条动画来覆盖
        self.progressbar["maximum"] = 50  # 重置进度条长度，值越小加载动画越快
        self.progressbar['mode'] = 'indeterminate'  # 进度条为来回动模式
        self.progressbar.start()  # 进度条开始加载动画
        Config.set('tipsTop2', '快捷识图中……')
        # 输出初始信息
        startStr = f"\n快捷识图 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n\n"
        self.outputPanel.print(startStr)

    def onGet(self, numData, ocrData):
        # ==================== 分析文块 ====================
        if ocrData['code'] == 100:  # 成功
            tbList = ocrData['data']  # 获取文块
            # 将文块组导入每一个文块处理器，获取输出文块组
            for proc in self.procList:
                tbList, s = proc.run(tbList, None)
            tbStr = ''
            for tb in tbList:
                tbStr += tb['text']+'\n'
            self.outputPanel.print(tbStr+'\n')  # 输出到面板
            if Config.get('isNeedCopy'):  # 需要复制
                if tbStr and tbStr[-1] == '\n':
                    pyperclipCopy(tbStr[:-1])  # 去除结尾空格，复制到剪贴板
        elif ocrData['code'] == 101:  # 无文字
            self.outputPanel.print('未发现文字\n')
        else:  # 识别失败
            self.outputPanel.print(
                f'识别失败，错误码：{ocrData["code"]}\n错误信息：{str(ocrData["data"])}\n')
        Config.set('tipsTop1', f'{round(numData["time"], 2)}s ')

    def onStop(self, num):
        self.setRunning(MsnFlag.none)
