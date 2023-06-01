# ========================================
# =============== 批量OCR页 ===============
# ========================================

import os
from .page import Page


class BatchOCR(Page):

    def findImages(self, paths):  # 接收路径列表，在路径中搜索图片
        suf = [".jpg", ".jpe", ".jpeg", ".jfif",
               ".png", ".webp", ".bmp", ".tif", ".tiff"]

        def isImg(path):  # 路径是图片返回true
            return os.path.splitext(path)[-1].lower() in suf

        imgPaths = []
        for p in paths:
            if os.path.isfile(p) and isImg(p):  # 是文件，直接判断
                imgPaths.append(os.path.abspath(p))
            elif os.path.isdir(p):  # 是路径
                for root, dirs, files in os.walk(p):
                    for file in files:
                        if isImg(file):  # 收集子文件
                            imgPaths.append(os.path.abspath(
                                os.path.join(root, file)))  # 将路径转换为绝对路径
                    for dir in dirs:  # 继续搜索子目录
                        paths.append(os.path.join(root, dir))
        for i, p in enumerate(imgPaths):  # 规范化正斜杠
            imgPaths[i] = p.replace("\\", "/")
        return imgPaths
