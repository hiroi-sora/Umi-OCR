# 单独txt文件

from .output import Output


class OutputTxtIndividual(Output):
    def openOutputFile(self):
        pass  # 覆盖父类方法

    def print(self, res):  # 输出图片结果
        if not res["code"] == 100 and self.ingoreBlank:
            return  # 忽略空白图片
        textOut = ""
        if res["code"] == 100:
            for r in res["data"]:
                textOut += r["text"] + "\n"
        elif res["code"] == 101:
            pass
        else:
            textOut += f'[Error] OCR failed. Code: {res["code"]}, Msg: {res["data"]}\n【异常】OCR识别失败。\n'
        path = res["path"] + ".txt"  # 同名路径+txt
        with open(path, "w", encoding="utf-8") as f:  # 追加写入同名本地文件
            f.write(textOut)
