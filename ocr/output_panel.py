# 输出到软件面板
from utils.config import Config
from ocr.output import Output

from utils.logger import GetLog
Log = GetLog()


class OutputPanel(Output):

    def __init__(self):
        self.panelOutput = Config.get('panelOutput')  # 输出接口
        self.isDebug = Config.get('isDebug')  # 是否输出调试
        self.outputPath = Config.get('outputFilePath')  # 输出文件夹，用于计划任务的完成后打开文件夹

    def print(self, text):
        self.panelOutput(text)

    def debug(self, text):
        '''输出调试信息'''
        self.print(f'[调试信息] {text}')

    def text(self, text):
        '''输出正文'''
        self.print(text)

    def img(self, textBlockList, imgInfo, numData, textDebug):
        '''输出图片结果'''
        # 标题和debug信息
        textDebug = f'{textDebug}\n\n' if self.isDebug and textDebug else ''
        textOut = f'\n{imgInfo["name"]}\n\n{textDebug}'
        # 正文
        for tb in textBlockList:
            if tb['text']:
                textOut += f'{tb["text"]}\n'
        self.print(textOut+'\n')
