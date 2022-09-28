# 输出器的基类。按指定的格式，将传入的文本输出到指定地方。

from utils.logger import GetLog

import os

Log = GetLog()


class Output:
    def __init__(self):
        self.outputPath = ''  # 输出路径

    def print(self, text):
        '''直接输出文字'''
        Log.info(f'输出: {text}')

    def openOutputFile(self):
        '''打开输出文件（夹）'''
        if self.outputPath and os.path.exists(self.outputPath):
            os.startfile(self.outputPath)
