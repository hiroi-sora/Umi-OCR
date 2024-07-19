# 排版解析-单栏-单行

from .tbpu import Tbpu
from .parser_tools.line_preprocessing import linePreprocessing  # 行预处理
from .parser_tools.paragraph_parse import word_separator  # 上下句间隔符


class SingleLine(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-单栏-单行"

    # 从文本块列表中找出所有行
    def get_lines(self, textBlocks):
        # 按x排序
        textBlocks.sort(key=lambda tb: tb["normalized_bbox"][0])
        lines = []
        for i1, tb1 in enumerate(textBlocks):
            if not tb1:
                continue
            # 最左的一个块
            l1, top1, r1, bottom1 = tb1["normalized_bbox"]
            h1 = bottom1 - top1
            now_line = [tb1]
            # 考察右侧哪些块符合条件
            for i2 in range(i1 + 1, len(textBlocks)):
                tb2 = textBlocks[i2]
                if not tb2:
                    continue
                l2, top2, r2, bottom2 = tb2["normalized_bbox"]
                h2 = bottom2 - top2
                # 行2左侧太前
                if l2 < r1 - h1:
                    continue
                # 垂直距离太远
                if top2 < top1 - h1 * 0.5 or bottom2 > bottom1 + h1 * 0.5:
                    continue
                # 行高差距过大
                if abs(h1 - h2) > min(h1, h2) * 0.5:
                    continue
                # 符合条件
                now_line.append(tb2)
                textBlocks[i2] = None
                # 更新搜索条件
                r1 = r2
            # 处理完一行
            for i2 in range(len(now_line) - 1):
                # 检查同一行内相邻文本块的水平间隙
                l1, t1, r1, b1 = now_line[i2]["normalized_bbox"]
                l2, t2, r2, b2 = now_line[i2 + 1]["normalized_bbox"]
                h = (b1 + b2 - t1 - l2) * 0.5
                if l2 - r1 > h * 1.5:  # 间隙太大，强制设置空格
                    now_line[i2]["end"] = " "
                    continue
                letter1 = now_line[i2]["text"][-1]
                letter2 = now_line[i2 + 1]["text"][0]
                now_line[i2]["end"] = word_separator(letter1, letter2)
            now_line[-1]["end"] = "\n"
            lines.append(now_line)
            textBlocks[i1] = None
        # 所有行按y排序
        lines.sort(key=lambda tbs: tbs[0]["normalized_bbox"][1])
        return lines

    def run(self, textBlocks):
        textBlocks = linePreprocessing(textBlocks)  # 预处理
        lines = self.get_lines(textBlocks)  # 获取每一行
        # 解包
        textBlocks = []
        for line in lines:
            for tb in line:
                del tb["normalized_bbox"]
                textBlocks.append(tb)
        return textBlocks
