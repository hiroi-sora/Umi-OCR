# 合并：段落-横排-代码段（还原空格间距）


from .tbpu import Tbpu


class MergeParaCode(Tbpu):
    def __init__(self):
        super().__init__()
        self.tbpuName = "多行-代码段"
        self.mllhY = 0.5  # 单行合并时的垂直距离偏差阈值
        self.indentation = 0.5  # 多行合并时，缩进

    def merge2box(self, A, B):  # 两个文块属于同一行时，返回 True
        yTop = min(A[0][1], A[1][1], B[0][1], B[1][1])
        yBottom = max(A[2][1], A[3][1], B[2][1], B[3][1])
        xLeft = min(A[0][0], A[3][0], B[0][0], B[3][0])
        xRight = max(A[1][0], A[2][0], B[1][0], B[2][0])
        A[0][1] = A[1][1] = yTop  # y上
        A[2][1] = A[3][1] = yBottom  # y下
        A[0][0] = A[3][0] = xLeft  # x左
        A[1][0] = A[2][0] = xRight  # x右

    def mergeLine(self, textBlocks):  # 单行合并
        # 所有文块，按左上角点的x坐标排序
        textBlocks.sort(key=lambda tb: tb["box"][0][0])
        # 遍历每个文块，寻找后续文块中与它垂直接近的项，合并两个文块
        resList = []
        listlen = len(textBlocks)
        for iA in range(listlen):
            tA = textBlocks[iA]
            if not tA:
                continue
            A = tA["box"]
            num = 1  # 合并个数
            # 遍历后续文块
            for iB in range(iA + 1, listlen):
                tB = textBlocks[iB]
                if not tB:
                    continue
                B = tB["box"]
                Ay = A[1][1]  # 块A右上角y
                Ah = A[3][1] - A[0][1]  # 块A行高
                By = B[0][1]  # 块B左上角y
                ly = Ah * self.mllhY
                # 符合同一行，则合并
                if abs(By - Ay) < ly:
                    self.merge2box(A, B)
                    tA["text"] += (  # 合并文字时，补充与间距相同的空格数
                        " " * round((A[1][0] - A[0][0]) / (Ah * 2)) + tB["text"]
                    )
                    textBlocks[iB] = None  # 置为空，标记删除
                    num += 1
            if num > 1:
                tA["score"] /= num  # 平均置信度
            resList.append(tA)  # 装填入结果
        return resList

    def mergePara(self, textBlocks):  # 所有行合并
        # 单行合并
        textBlocks = self.mergeLine(textBlocks)
        # 按左上角y排序
        textBlocks.sort(key=lambda tb: tb["box"][0][1])
        # 提取每个文块的开头缩进长度，和行高平均数。
        leftList = []  # 起始列表
        lh = 0
        for tb in textBlocks:
            b = tb["box"]
            leftList.append(b[0][0])
            lh += b[3][1] - b[0][1]
        lh /= len(textBlocks)
        xMin = min(leftList)  # 最左侧起始
        xMax = max(leftList)  # 最右侧结束
        # 构建缩进层级列表
        levelList = []
        x = xMin
        while x < xMax:
            levelList.append(x)
            x += lh
        levelList.append(xMax + 1)
        # 合并所有行，按缩进层级加上开头空格
        text = ""
        score = 0
        num = 0
        box = None
        for tb in textBlocks:
            # 获取缩进层级
            level = 0
            b = tb["box"]
            for i in range(len(levelList) - 1):
                _min, _max = levelList[i], levelList[i + 1]
                if _min <= b[0][0] < _max:
                    level = i
                    break
            text += " " * level * 2 + tb["text"] + "\n"
            score += tb["score"]
            num += 1
            if not box:
                box = tb["box"]
            else:
                self.merge2box(box, tb["box"])
        if len(text) > 0:
            text = text[:-1]  # 去除尾部换行
        if num > 0:
            score /= num
        res = [{"text": text, "box": box, "score": score}]
        return res

    def run(self, textBlocks):
        # 段落合并
        resList = self.mergePara(textBlocks)
        # 返回新文块列表
        return resList
