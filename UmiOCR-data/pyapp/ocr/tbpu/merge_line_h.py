# 合并：横排-单行

from .tbpu import Tbpu

from functools import cmp_to_key

Punctuation = ".,;:!?"


class MergeLineH(Tbpu):
    def __init__(self):
        self.tbpuName = "横排-单行"
        # merge line limit multiple X/Y/H，单行合并时的水平/垂直/行高阈值系数，为行高的倍数
        self.mllhX = 2
        self.mllhY = 0.5
        self.mllhH = 0.5

    def isMerge(self, b1, b2):  # 两个文块符合合并条件时，返回 True
        b1x, b1y = b1[1][0], b1[1][1]  # 块1右上角xy
        b1h = b1[3][1] - b1[0][1]  # 块1行高
        b2x, b2y = b2[0][0], b2[0][1]  # 块2左上角xy
        b2h = b2[3][1] - b2[0][1]  # 块2行高
        lx = round(b1h * self.mllhX)  # 水平、垂直、行高 合并阈值
        ly = round(b1h * self.mllhY)
        lh = round(b1h * self.mllhH)
        if abs(b2x - b1x) < lx and abs(b2y - b1y) < ly and abs(b2h - b1h) < lh:
            return True
        return False

    def merge2text(self, text1, text2):  # 合并两段文字
        # a, b = text1[-1], text2[0]  # 两段的开头/结尾字符
        # if (
        #     a.isdigit()  # 数字
        #     or b.isdigit()  # 字符
        #     or a.isalpha()
        #     or b.isalpha()
        #     or a in Punctuation
        # ):
        #     return text1 + " " + text2
        return text1 + " " + text2

    def sortLines(self, resList):  # 对文块排序，从上到下，从左到右
        def sortKey(A, B):
            # 先比较两个文块的水平投影是否重叠
            ay1, ay2 = A["box"][0][1], A["box"][3][1]
            by1, by2 = B["box"][0][1], B["box"][3][1]
            # 不重叠，则按左上角y排序
            if ay2 < by1 or ay1 > by2:
                return 0 if ay1 == by1 else (-1 if ay1 < by1 else 1)
            # 重叠，则按左上角x排序
            ax, bx = A["box"][0][0], B["box"][0][0]
            return 0 if ax == bx else (-1 if ax < bx else 1)

        resList.sort(key=cmp_to_key(sortKey))

    def run(self, textBlocks, imgInfo):
        # 所有文块，按左上角点的x坐标排序
        textBlocks.sort(key=lambda tb: tb["box"][0][0])
        # 遍历每个文块，寻找后续文块中与它接壤、且行高一致的项，合并两个文块
        resList = []
        listlen = len(textBlocks)
        for index in range(listlen):
            tb1 = textBlocks[index]
            if not tb1:
                continue
            b1 = tb1["box"]
            num = 1  # 合并个数
            # 遍历后续文块
            for i in range(index + 1, listlen):
                tb2 = textBlocks[i]
                if not tb2:
                    continue
                b2 = tb2["box"]
                # 块1的右上角与块2的左上角接壤，且二者行高相近，则合并
                if self.isMerge(b1, b2):
                    num += 1
                    # 合并两个文块box
                    yTop = min(b1[0][1], b1[1][1], b2[0][1], b2[1][1])
                    yBottom = max(b1[2][1], b1[3][1], b2[2][1], b2[3][1])
                    b1[0][1] = b1[1][1] = yTop  # y上
                    b1[2][1] = b1[3][1] = yBottom  # y下
                    b1[0][0] = b1[3][0] = min(b1[0][0], b1[3][0])  # x左
                    b1[1][0] = b1[2][0] = max(b2[1][0], b2[2][0])  # x右
                    # 合并内容
                    tb1["score"] += tb2["score"]  # 合并置信度
                    tb1["text"] = self.merge2text(tb1["text"], tb2["text"])  # 合并文本
                    textBlocks[i] = None  # 置为空，标记删除
            if num > 1:
                tb1["score"] /= num  # 平均置信度
            resList.append(tb1)  # 装填入结果
        # 结果排序
        self.sortLines(resList)
        # 返回新文块组和debug字符串
        return resList
