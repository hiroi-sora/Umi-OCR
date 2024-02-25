# 排版解析-单栏-代码段

from .parser_single_line import SingleLine
from .parser_tools.line_preprocessing import linePreprocessing  # 行预处理

from bisect import bisect_left


class SingleCode(SingleLine):
    def __init__(self):
        self.tbpuName = "排版解析-单栏-代码段"

    def merge_line(self, line):  # 合并一行
        A = line[0]
        ba = A["box"]
        ha = ba[3][1] - ba[0][1]  # 块A行高
        score = A["score"]
        for i in range(1, len(line)):
            B = line[i]
            bb = B["box"]
            ha = (ha + bb[3][1] - bb[0][1]) / 2
            # 合并文字，补充与间距相同的空格数
            space = 0
            if bb[0][0] > ba[1][0]:
                space = round((bb[0][0] - ba[1][0]) / ha)
            A["text"] += "  " * space + B["text"]
            print(space, bb[0][0], ba[1][0])
            # 合并包围盒
            yTop = min(ba[0][1], ba[1][1], bb[0][1], bb[1][1])
            yBottom = max(ba[2][1], ba[3][1], bb[2][1], bb[3][1])
            xLeft = min(ba[0][0], ba[3][0], bb[0][0], bb[3][0])
            xRight = max(ba[1][0], ba[2][0], bb[1][0], bb[2][0])
            ba[0][1] = ba[1][1] = yTop  # y上
            ba[2][1] = ba[3][1] = yBottom  # y下
            ba[0][0] = ba[3][0] = xLeft  # x左
            ba[1][0] = ba[2][0] = xRight  # x右
            # 置信度
            score += B["score"]
        A["score"] = score / len(line)
        del A["normalized_bbox"]
        A["end"] = "\n"
        return A

    def indent(self, tbs):  # 分析所有行，构造缩进
        lh = 0  # 平均行高
        xMin = float("inf")  # 句首的最左、最右x值
        xMax = float("-inf")
        for tb in tbs:
            b = tb["box"]
            lh += b[3][1] - b[0][1]
            x = b[0][0]
            xMin = min(xMin, x)
            xMax = max(xMax, x)
        lh /= len(tbs)
        lh2 = lh / 2
        # 构建缩进层级列表
        levelList = []
        x = xMin
        while x < xMax:
            levelList.append(x)
            x += lh
        # 按照层级，为每行句首加上空格，并调整包围盒
        for tb in tbs:
            b = tb["box"]
            level = bisect_left(levelList, b[0][0] + lh2) - 1  # 二分查找层级点
            tb["text"] = "  " * level + tb["text"]  # 补充空格
            b[0][0] = b[3][0] = xMin  # 左侧归零

    def run(self, textBlocks):
        textBlocks = linePreprocessing(textBlocks)  # 预处理
        lines = self.get_lines(textBlocks)  # 获取每一行
        tbs = [self.merge_line(line) for line in lines]  # 合并所有行
        self.indent(tbs)  # 为每行添加句首缩进
        return tbs
