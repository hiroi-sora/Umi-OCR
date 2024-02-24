# 排版解析-多栏-无换行

from .tbpu import Tbpu
from .parser_tools.line_preprocessing import linePreprocessing  # 行预处理
from .parser_tools.gap_tree import GapTree  # 间隙树排序算法
from .parser_tools.paragraph_parse import word_separator  # 上下句间隔符


class MultiNone(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-多栏-无换行"

        # 构建算法对象，指定包围盒的元素位置
        self.gtree = GapTree(lambda tb: tb["normalized_bbox"])

    def run(self, textBlocks):
        textBlocks = linePreprocessing(textBlocks)  # 预处理
        textBlocks = self.gtree.sort(textBlocks)  # 构建间隙树
        # 补充行尾间隔符
        for i in range(len(textBlocks)):
            tb = textBlocks[i]
            if i < len(textBlocks) - 1:
                letter1 = tb["text"][-1]  # 行1结尾字母
                letter2 = textBlocks[i + 1]["text"][0]  # 行2开头字母
                tb["end"] = word_separator(letter1, letter2)  # 获取间隔符
            else:
                tb["end"] = "\n"
            del tb["normalized_bbox"]
        return textBlocks
