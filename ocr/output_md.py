# 输出到txt文件
from utils.config import Config
from ocr.output import Output
from utils.logger import GetLog

import os

Log = GetLog()


class OutputMD(Output):

    def __init__(self):
        outputDir = Config.get('outputFilePath')  # 输出路径（文件夹）
        outputName = Config.get("outputFileName")  # 文件名
        self.outputPath = f'{outputDir}/{outputName}.md'  # 输出路径
        self.isDebug = Config.get('isDebug')  # 是否输出调试
        # 创建输出文件
        try:
            if os.path.exists(self.outputPath):  # 文件存在
                os.remove(self.outputPath)  # 删除文件
            open(self.outputPath, 'w').close()  # 创建文件
        except FileNotFoundError:
            raise Exception(f'创建md文件失败。请检查以下地址是否正确。\n{self.outputPath}')
        except Exception as e:
            raise Exception(
                f'创建txt文件失败。文件地址：\n{self.outputPath}\n\n错误信息：\n{e}')

    def print(self, text):
        if self.outputPath:
            with open(self.outputPath, "a", encoding='utf-8') as f:  # 追加写入本地文件
                f.write(text)

    def debug(self, text):
        '''输出调试信息'''
        self.print(f'```\n{text}```\n')

    def text(self, text):
        '''输出正文'''
        textList = text.split('\n')  # 按行拆分
        outStr = ''
        for t in textList:
            if t:
                outStr += f'> {t}  \n'  # 每一行加引用号
        self.print(f'{outStr}')

    def img(self, textBlockList, imgInfo, numData, textDebug):
        '''输出图片结果'''
        # 标题和debug信息
        textDebug = f'```\n{textDebug}```\n' if self.isDebug and textDebug else ''
        name = imgInfo["name"]
        path = name.replace(" ", "%20")  # 空格转 %20
        textOut = f'\n---\n![{name}]({path})\n[{name}]({path})\n\n{textDebug}'
        # 正文
        for tb in textBlockList:
            if tb['text']:
                textOut += f'> {tb["text"]}  \n'  # 每一行加引用号
        self.print(textOut+'\n')
