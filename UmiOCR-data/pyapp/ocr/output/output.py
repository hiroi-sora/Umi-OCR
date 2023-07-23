# OCR输出器的基类。按指定的格式，将传入的文本输出到指定地方。

import os


class Output:
    def __init__(self):
        self.outputPath = ""  # 输出路径

    def print(self, res):
        """输出图片信息"""
        textOut = f"图片路径：{res['path']}\n代码：{res['code']}\n"
        if res["code"] == 100:
            for r in res["data"]:
                textOut += r["text"]
        elif res["code"] == 101:
            textOut += "无文字"
        else:
            textOut += f"错误原因：{res['data']}"
        print(textOut)

    def openOutputFile(self):
        """打开输出文件（夹）"""
        if self.outputPath and os.path.exists(self.outputPath):
            os.startfile(self.outputPath)
