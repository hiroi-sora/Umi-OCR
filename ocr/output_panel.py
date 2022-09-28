# 输出到软件面板
from utils.config import Config
from ocr.output import Output

from utils.logger import GetLog
Log = GetLog()


class OutputPanel(Output):

    def __init__(self):
        self.panelOutput = Config.main.panelOutput  # 输出接口
        self.isDebug = Config.get('isDebug')  # 是否输出调试
        self.outputPath = Config.get('outputFilePath')  # 输出文件夹，用于计划任务的完成后打开文件夹

    def print(self, text, highlight=''):
        self.panelOutput(text, highlight=highlight)

    def debug(self, text):
        '''输出调试信息'''
        self.print(f'[调试信息] {text}')

    def text(self, text):
        '''输出正文'''
        self.print(text)

    def img(self, textBlockList, imgInfo, numData, textDebug):
        '''输出图片结果'''
        # 输出标题
        self.print('\n')
        self.print(imgInfo['name'], highlight='blue')  # 高亮输出文件名
        # debug信息
        textOut = '\n\n'
        if self.isDebug and textDebug:
            textOut += textDebug
        # 正文
        for tb in textBlockList:
            if tb['text']:
                textOut += f'{tb["text"]}\n'
        self.print(textOut+'\n')
