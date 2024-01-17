# 输出到txt文件

from .output import Output


class OutputTxt(Output):
    def __init__(self, argd):
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.txt"  # 输出路径
        self.ingoreBlank = argd["ingoreBlank"]  # 忽略空白文件
        # 创建输出文件
        try:
            with open(self.outputPath, "w", encoding="utf-8") as f:  # 覆盖创建文件
                f.write(f'{argd["startDatetime"]}\n\n')  # 写入开始时间日期
        except Exception as e:
            raise Exception(f"Failed to create txt file. {e}\n创建txt文件失败。")

    def print(self, res):  # 输出图片结果
        if not res["code"] == 100 and self.ingoreBlank:
            return  # 忽略空白图片
        textOut = f'≦ {res["fileName"]} ≧\n'
        if res["code"] == 100:
            for r in res["data"]:
                textOut += r["text"] + "\n"
        elif res["code"] == 101:
            pass
        else:
            textOut += f'[Error] OCR failed. Code: {res["code"]}, Msg: {res["data"]}\n【异常】OCR识别失败。\n'
        textOut += "\n"  # 多空一行
        with open(self.outputPath, "a", encoding="utf-8") as f:  # 追加写入本地文件
            f.write(textOut)
