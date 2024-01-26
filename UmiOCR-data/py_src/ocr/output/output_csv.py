# 输出到csv表格文件

from .output import Output

import csv


class OutputCsv(Output):
    def __init__(self, argd):
        self.encoding = "ansi"  # 保存编码，要兼容Office
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.csv"  # 输出路径
        self.ingoreBlank = argd["ingoreBlank"]  # 忽略空白文件
        self.headers = ["Image Name", "OCR", "Image Path"]  # 表头
        # 创建输出文件
        try:
            with open(
                self.outputPath, "w", encoding="utf-8", newline=""
            ) as f:  # 覆盖创建文件
                writer = csv.writer(f)
                writer.writerow(self.headers)  # 写入CSV表头
        except Exception as e:
            raise Exception(f"Failed to create csv file. {e}\n创建csv文件失败。")

    def print(self, res):  # 输出图片结果
        if not res["code"] == 100 and self.ingoreBlank:
            return  # 忽略空白图片
        name = res["fileName"]
        path = res["path"]
        textOut = ""
        if res["code"] == 100:
            datas = res["data"]
            last = len(datas) - 1
            for i, tb in enumerate(datas):
                textOut += tb["text"]
                if i < last:
                    textOut += tb["end"]
        elif res["code"] == 101:
            pass
        else:
            textOut += f'[Error] OCR failed. Code: {res["code"]}, Msg: {res["data"]}  \n【异常】OCR识别失败。'

        writeList = [name, textOut, path]
        with open(
            self.outputPath, "a", encoding=self.encoding, newline="", errors="ignore"
        ) as f:  # 追加写入本地文件
            writer = csv.writer(f)
            writer.writerow(writeList)
