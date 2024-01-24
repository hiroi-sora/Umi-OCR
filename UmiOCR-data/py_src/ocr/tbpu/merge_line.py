# 合并：单行-横排

from .tbpu import Tbpu

from functools import cmp_to_key


class MergeLine(Tbpu):
    def __init__(self):
        self.tbpuName = "单行-横排"
        # merge line limit multiple X/Y/H，单行合并时的水平/垂直/行高阈值系数，为行高的倍数
        self.mllhX = 2
        self.mllhY = 0.5
        self.mllhH = 0.5

    def isSameLine(self, A, B):  # 两个文块属于同一行时，返回 True
        Ax, Ay = A[1][0], A[1][1]  # 块A右上角xy
        Ah = A[3][1] - A[0][1]  # 块A行高
        Bx, By = B[0][0], B[0][1]  # 块B左上角xy
        Bh = B[3][1] - B[0][1]  # 块B行高
        lx = Ah * self.mllhX  # 水平、垂直、行高 合并阈值
        ly = Ah * self.mllhY
        lh = Ah * self.mllhH
        if abs(Bx - Ax) < lx and abs(By - Ay) < ly and abs(Bh - Ah) < lh:
            return True
        return False

    def merge2tb(self, textBlocks, i1, i2, separator):  # 合并2个tb，将i2合并到i1中。
        tb1 = textBlocks[i1]
        tb2 = textBlocks[i2]
        b1 = tb1["box"]
        b2 = tb2["box"]
        # 合并两个文块box
        yTop = min(b1[0][1], b1[1][1], b2[0][1], b2[1][1])
        yBottom = max(b1[2][1], b1[3][1], b2[2][1], b2[3][1])
        xLeft = min(b1[0][0], b1[3][0], b2[0][0], b2[3][0])
        xRight = max(b1[1][0], b1[2][0], b2[1][0], b2[2][0])
        b1[0][1] = b1[1][1] = yTop  # y上
        b1[2][1] = b1[3][1] = yBottom  # y下
        b1[0][0] = b1[3][0] = xLeft  # x左
        b1[1][0] = b1[2][0] = xRight  # x右
        # 合并内容
        tb1["score"] += tb2["score"]  # 合并置信度
        tb1["text"] = tb1["text"] + separator + tb2["text"]  # 合并文本
        textBlocks[i2] = None  # 置为空，标记删除

    def mergeLine(self, textBlocks):  # 单行合并
        # 所有文块，按左上角点的x坐标排序
        textBlocks.sort(key=lambda tb: tb["box"][0][0])
        # 遍历每个文块，寻找后续文块中与它接壤、且行高一致的项，合并两个文块
        resList = []
        listlen = len(textBlocks)
        for i1 in range(listlen):
            tb1 = textBlocks[i1]
            if not tb1:
                continue
            b1 = tb1["box"]
            num = 1  # 合并个数
            # 遍历后续文块
            for i2 in range(i1 + 1, listlen):
                tb2 = textBlocks[i2]
                if not tb2:
                    continue
                b2 = tb2["box"]
                # 符合同一行，则合并
                if self.isSameLine(b1, b2):
                    # 合并两个文块box
                    self.merge2tb(textBlocks, i1, i2, " ")
                    num += 1
            if num > 1:
                tb1["score"] /= num  # 平均置信度
            resList.append(tb1)  # 装填入结果
        return resList

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

    def run(self, textBlocks):
        # 单行合并
        resList = self.mergeLine(textBlocks)
        # 结果排序
        self.sortLines(resList)
        # 返回新文块列表
        return resList
