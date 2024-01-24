# 合并：段落-横排-自然段

from .merge_line import MergeLine


class MergePara(MergeLine):
    def __init__(self):
        super().__init__()
        self.tbpuName = "多行-自然段"
        self.mllhLine = 1.8  # 最大段间距

    def isSameColumn(self, A, B):  # 两个文块属于同一栏时，返回 True
        # 获取A、B行高
        if "lineHeight" in A:  # 已记录
            Ah = A["lineHeight"]
        else:  # 未记录，则写入记录
            Ah = A["lineHeight"] = A["box"][3][1] - A["box"][0][1]
            A["lineCount"] = 1  # 段落的行数
        Bh = B["box"][3][1] - B["box"][0][1]
        if abs(Bh - Ah) > Ah * self.mllhH:
            return False  # AB行高不符
        # 行高相符，判断垂直投影是否重叠
        ax1, ax2 = A["box"][0][0], A["box"][1][0]
        bx1, bx2 = B["box"][0][0], B["box"][1][0]
        if ax2 < bx1 or ax1 > bx2:
            return False
        return True  # AB垂直投影重叠

    def isSamePara(self, A, B):  # 两个文块属于同一段落时，返回 True
        ah = A["lineHeight"]
        # 判断垂直距离
        ly = ah * self.mllhY
        lLine = ah * self.mllhLine
        a, b = A["box"], B["box"]
        ay, by = a[3][1], b[0][1]
        if by < ay - ly or by > ay + lLine:
            return False  # 垂直距离过大
        # 判断水平距离
        lx = ah * self.mllhX
        ax, bx = a[0][0], b[0][0]
        if A["lineCount"] == 1:  # 首行允许缩进2格
            return ax - ah * 2.5 - lx <= bx <= ax + lx
        else:
            return abs(ax - bx) <= lx

    def merge2line(self, textBlocks, i1, i2):  # 合并2行
        ranges = [
            (0x4E00, 0x9FFF),  # 汉字
            (0x3040, 0x30FF),  # 日文
            (0xAC00, 0xD7AF),  # 韩文
            (0xFF01, 0xFF5E),  # 全角字符
        ]
        # 判断两端文字的结尾和开头，是否属于汉藏语族
        # 汉藏语族：行间无需分割符。印欧语族：则两行之间需加空格。
        separator = " "
        ta, tb = textBlocks[i1]["text"][-1], textBlocks[i2]["text"][0]
        fa, fb = False, False
        for l, r in ranges:
            if l <= ord(ta) <= r:
                fa = True
            if l <= ord(tb) <= r:
                fb = True
        if fa and fb:
            separator = ""
        #     print(f"【{ta}】与【{tb}】是汉字集。")
        # else:
        #     print(f"【{ta}】与【{tb}】是西文集。")
        self.merge2tb(textBlocks, i1, i2, separator)
        textBlocks[i1]["lineCount"] += 1  # 行数+1

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
            num = 1  # 合并个数
            # 遍历后续文块
            for i2 in range(i1 + 1, listlen):
                tb2 = hList[i2]
                if not tb2:
                    continue
                # 符合同一栏
                if self.isSameColumn(tb1, tb2):
                    # 符合同一段，合并两行
                    if self.isSamePara(tb1, tb2):
                        self.merge2line(hList, i1, i2)
                        num += 1
                    # 同栏、不同段，说明到了下一段，则退出内循环
                    else:
                        break
            if num > 1:
                tb1["score"] /= num  # 平均置信度
            resList.append(tb1)  # 装填入结果
        return resList

    def run(self, textBlocks):
        # 段落合并
        resList = self.mergePara(textBlocks)
        # 返回新文块列表
        return resList
