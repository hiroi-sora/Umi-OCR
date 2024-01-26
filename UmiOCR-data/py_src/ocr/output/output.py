# OCR输出器的基类。按指定的格式，将传入的文本输出到指定地方。

from ...platform import Platform
import os


class Output:
    def __init__(self, argd):
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.txt"  # 输出路径
        self.ingoreBlank = argd["ingoreBlank"]  # 忽略空白文件

    def print(self, res):  # 输出图片信息
        if not res["code"] == 100 and self.ingoreBlank:
            return  # 忽略空白图片
        textOut = f"图片路径：{res['path']}\n代码：{res['code']}\n"
        if res["code"] == 100:
            datas = res["data"]
            last = len(datas) - 1
            for i, tb in enumerate(datas):
                textOut += tb["text"]
                if i < last:
                    textOut += tb["end"]
        elif res["code"] == 101:
            textOut += "无文字"
        else:
            textOut += f"错误原因：{res['data']}"
        print(textOut)

    def openOutputFile(self):  # 打开输出文件
        if self.outputPath and os.path.exists(self.outputPath):
            Platform.startfile(self.outputPath)

    def onEnd(self):  # 结束输出。
        pass
