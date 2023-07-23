# 输出到txt文件

import os
from .output import Output


class OutputTxt(Output):
    def __init__(self, dir, fileName, startDatetime):
        self.dir = dir  # 输出路径（文件夹）
        self.fileName = fileName  # 文件名
        self.outputPath = f"{dir}/{fileName}.txt"  # 输出路径
        # 创建输出文件
        try:
            with open(self.outputPath, "w", encoding="utf-8") as f:  # 覆盖创建文件
                f.write(f"{startDatetime}\n\n")  # 写入开始时间戳
        except FileNotFoundError:
            raise Exception(f"创建txt文件失败。请检查以下地址是否正确。\n{self.outputPath}")
        except Exception as e:
            raise Exception(f"创建txt文件失败。文件地址：\n{self.outputPath}\n\n错误信息：\n{e}")

    def print(self, res):  # 输出图片结果
        """输出图片信息"""
        textOut = f'≦ {res["fileName"]} ≧\n'
        if res["code"] == 100:
            for r in res["data"]:
                textOut += r["text"] + "\n"
        elif res["code"] == 101:
            textOut += "[Message] No Text. \n【通知】图片中未找到文字。\n"
        else:
            textOut += f'[Error] OCR failed. Code: {res["code"]}, Msg: {res["data"]}\n【异常】OCR识别失败。\n'
        textOut += "\n"  # 多空一行
        with open(self.outputPath, "a", encoding="utf-8") as f:  # 追加写入本地文件
            f.write(textOut)
