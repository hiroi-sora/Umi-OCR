import subprocess
import json


class OCR:

    def __init__(self, exePath="PaddleOCR_json.exe"):
        """初始化识别器。\n
        传入识别器exe路径。"""
        self.ret = subprocess.Popen(  # 打开管道
            exePath,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        self.ret.stdout.readline()  # 读掉第一行

    def run(self, imgPath):
        """对一张图片文字识别。
        输入图片路径。\n
        识别成功时，返回列表，每项是一组文字的信息。\n
        识别失败时，返回字典 {error:异常信息，text:(若存在)原始识别字符串} 。"""
        if not imgPath[-1] == "\n":
            imgPath += "\n"
        self.ret.stdin.write(imgPath.encode("gbk"))
        self.ret.stdin.flush()
        getStr = self.ret.stdout.readline().decode('utf-8', errors='ignore')
        try:
            return json.loads(getStr)
        except Exception as e:
            return {"error": e, "text": getStr}


if __name__ == "__main__":
    oCN = OCR()  # 默认路径识别器
    oJP = OCR("PaddleOCR_json_jp.exe")  # 日文识别器
    while True:
        p = input("请输入图片路径：\n")
        if input("本图片识别为中文（敲回车）还是日文（敲1）：") == "":
            dic = oCN.run(p)
        else:
            dic = oJP.run(p)
        if isinstance(dic, dict):
            print("识别失败，原因：", dic["error"])
            if "text" in dic:
                print("原始数据：\n", dic["text"])
        else:
            for i in dic:
                print(f'''
{i["text"]}
    左上角：{i["box"][0]},{i["box"][1]}
    右下角：{i["box"][4]},{i["box"][5]}
    置信度：{i["score"]}
    ''')
