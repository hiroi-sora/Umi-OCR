# 合并：段落-横排-左对齐

from .merge_line_h import MergeLineH


class MergeParaHLeft(MergeLineH):
    def __init__(self):
        super().__init__()
        self.tbpuName = "段落-横排-左对齐"

    def isSameColumn(self, A, B):  # 两个文块属于同一栏时，返回 True
        pass

    def isSamePara(self, A, B):  # 两个文块属于同一段落时，返回 True
        pass

    def mergePara(self, textBlocks):
        # 单行合并
        hList = self.mergeLine(textBlocks)
        # 按左上角y排序
        hList.sort(key=lambda tb: tb["box"][0][1])
        # 遍历每个行，寻找并合并属于同一段落的两个行
        listlen = len(hList)
        resList = []
        for i1 in range(listlen):
            tb1 = hList[i1]
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
                # 符合同一栏
                if self.isSameLine(b1, b2):
                    # 符合同一段，合并两行
                    if self.isSamePara(b1, b2):
                        self.merge2tb(textBlocks, i1, i2)
                        num += 1
                    # 同栏、不同段，说明到了下一段，则退出内循环
                    else:
                        break
            if num > 1:
                tb1["score"] /= num  # 平均置信度
            resList.append(tb1)  # 装填入结果
        return resList

    def run(self, textBlocks, imgInfo):
        # 段落合并
        resList = self.mergePara(textBlocks)
        # 返回新文块列表
        return resList
