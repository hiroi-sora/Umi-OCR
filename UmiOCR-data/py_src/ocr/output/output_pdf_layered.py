# 双层可搜索PDF

from .output import Output

import os
import fitz  # PyMuPDF


class OutputPdfLayered(Output):
    def __init__(self, argd):
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.originPath = argd["originPath"]  # 原始文件路径
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.layered.pdf"  # 输出路径
        # 加载pymupdf对象
        try:
            self.pdf = fitz.open(self.originPath)
        except Exception as e:
            self.pdf = None
            raise Exception(
                f"Failed to open doc file. {e}\n无法打开原始文档。\n{self.originPath}"
            )

    def print(self, res):  # 输出图片结果
        if not self.pdf:
            print("[Error] PDF对象未初始化！")
            return
        if not res["code"] == 100:
            return  # 忽略空白

        pno = res["page"] - 1  # 当前页数
        page = self.pdf[pno]  # 当前页对象
        page.clean_contents()  # 清空内容
        for tb in res["data"]:
            box = tb["box"]
            x0, y0 = box[0]
            x2, y2 = box[2]
            h = y2 - y0
            page.insert_text((x0, y0 + h), tb["text"], fontsize=h, fontname="china-ss")

    def onEnd(self):  # 结束时保存。
        print("保存PDF：", self.outputPath)
        if self.pdf:
            self.pdf.save(self.outputPath)
