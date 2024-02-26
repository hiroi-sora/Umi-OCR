# 输出到csv表格文件

from .output import Output
from .tools import getDataText

import csv


class OutputCsv(Output):
    def __init__(self, argd):
        self.encodings = [  # 保存编码优先级
            "ansi",  # Windows系统本地编码。在linux和macos下会抛出异常
            "ascii",  # 纯英
            "gbk",  # 简中
            "big5",  # 繁中
            "shift_jis",  # 日文
            "euc-kr",  # 韩文
            "utf-8",
        ]
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.csv"  # 输出路径
        self.ingoreBlank = argd["ingoreBlank"]  # 忽略空白文件
        self.writeLists = []  # 输出内容列表
        self.writeText = ""  # 输出内容字符串
        try:  # 覆盖创建临时文件
            with open(self.outputPath, "w", encoding="utf-8") as f:
                pass
        except Exception as e:
            raise Exception(f"Failed to create csv file. {e}\n创建csv文件失败。")

    def print(self, res):  # 输出图片结果
        if not res["code"] == 100 and self.ingoreBlank:
            return  # 忽略空白图片
        name = res["fileName"]
        path = res["path"]
        if res["code"] == 100:
            textOut = getDataText(res["data"])  # 获取拼接结果
        elif res["code"] == 101:
            textOut = ""
        else:
            textOut = f'[Error] OCR failed. Code: {res["code"]}, Msg: {res["data"]} .\n'
        self.writeLists.append([name, textOut, path])
        self.writeText += textOut

    def onEnd(self):  # 结束时保存。
        # 顺序测试编码优先级列表，获取保存编码
        encoding = "utf-8"
        for e in self.encodings:
            try:
                self.writeText.encode(e)
                encoding = e
                break
            # except UnicodeEncodeError:
            except Exception:
                pass
        print(f"Csv 保存编码： {encoding}")
        # 创建文件、输出
        headers = ["Name", "OCR", "Path"]  # 表头
        try:
            with open(
                self.outputPath, "w", encoding=encoding, newline=""
            ) as f:  # 覆盖创建文件
                writer = csv.writer(f)
                writer.writerow(headers)  # 写入CSV表头
                for writeList in self.writeLists:
                    writer.writerow(writeList)  # 写入CSV内容
        except Exception as e:
            raise Exception(f"Failed to write csv file. {e}\n写入csv文件失败。")
