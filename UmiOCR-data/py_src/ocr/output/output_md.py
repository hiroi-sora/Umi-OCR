# 输出markdown格式

from .output import Output

import os


class OutputMD(Output):
    def __init__(self, argd):
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.md"  # 输出路径
        self.ingoreBlank = argd["ingoreBlank"]  # 忽略空白文件
        # 创建输出文件
        try:
            with open(self.outputPath, "w", encoding="utf-8") as f:  # 覆盖创建文件
                f.write(f'> {argd["startDatetime"]}\n\n')
        except Exception as e:
            raise Exception(f"Failed to create jsonl file. {e}\n创建jsonl文件失败。")

    def print(self, res):  # 输出图片结果
        if not res["code"] == 100 and self.ingoreBlank:
            return  # 忽略空白图片
        name = res["fileName"]
        path = os.path.relpath(  # 从md文件到图片的相对路径
            res["path"], os.path.dirname(self.outputPath)
        )
        path = path.replace(" ", "%20")  # 空格转 %20
        textOut = f"""
---
![{name}]({path})
[{name}]({path})

"""
        # 正文
        if res["code"] == 100:
            texts = [""]
            datas = res["data"]
            for i, tb in enumerate(datas):
                if tb["end"] == "\n":
                    texts[-1] += tb["text"]
                    texts.append("")
                else:
                    texts[-1] += tb["text"] + tb["end"]
            print(f"原本{len(datas)}，处理后 {len(texts)}")
            for t in texts:
                textOut += f"> {t}  \n"
        elif res["code"] == 101:
            pass
        else:
            textOut += f'> [Error] OCR failed. Code: {res["code"]}, Msg: {res["data"]}  \n> 【异常】OCR识别失败。  \n'
        with open(self.outputPath, "a", encoding="utf-8") as f:  # 追加写入本地文件
            f.write(textOut)
