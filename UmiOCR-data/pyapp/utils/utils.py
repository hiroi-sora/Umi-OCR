import re
import os


# 传入文件名，检测是否含非法字符。没问题返回True
def allowedFileName(fn):
    pattern = r'[\\/:*?"<>|]'
    if re.search(pattern, fn):
        return False  # 转布尔值
    else:
        return True


# 传入路径列表，在路径中搜索图片。isRecurrence=True时递归搜索。
def findImages(paths, isRecurrence):
    # isRecurrence 递归读取
    suf = [
        ".jpg",
        ".jpe",
        ".jpeg",
        ".jfif",
        ".png",
        ".webp",
        ".bmp",
        ".tif",
        ".tiff",
    ]

    def isImg(path):  # 路径是图片返回true
        return os.path.splitext(path)[-1].lower() in suf

    imgPaths = []
    for p in paths:
        if os.path.isfile(p) and isImg(p):  # 是文件，直接判断
            imgPaths.append(os.path.abspath(p))
        elif os.path.isdir(p):  # 是路径
            if isRecurrence:  # 需要递归
                for root, dirs, files in os.walk(p):
                    print("dirs: ", dirs)
                    for file in files:
                        if isImg(file):  # 收集子文件
                            imgPaths.append(
                                os.path.abspath(os.path.join(root, file))
                            )  # 将路径转换为绝对路径
            else:  # 不递归读取子文件夹
                for file in os.listdir(p):
                    if os.path.isfile(os.path.join(p, file)) and isImg(file):
                        imgPaths.append(os.path.abspath(os.path.join(p, file)))
    for i, p in enumerate(imgPaths):  # 规范化正斜杠
        imgPaths[i] = p.replace("\\", "/")
    return imgPaths
