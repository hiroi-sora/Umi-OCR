import re


def allowedFileName(fn):  # 传入文件名，检测是否含非法字符。没问题返回True
    pattern = r'[\\/:*?"<>|]'
    if re.search(pattern, fn):
        return False  # 转布尔值
    else:
        return True
