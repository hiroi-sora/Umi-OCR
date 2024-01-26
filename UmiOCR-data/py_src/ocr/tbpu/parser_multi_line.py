# 排版解析-多栏-单行

from .tbpu import Tbpu
from .line_preprocessing import linePreprocessing  # 行预处理
from .gap_tree import GapTree  # 间隙树排序算法


class MultiLine(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-多栏-单行"

        def tb_bbox(tb):  # 从文本块对象中，提取左上角、右下角坐标元组
            # b = tb["box"]
            # return (b[0][0], b[0][1], b[2][0], b[2][1])
            return tb["normalized_bbox"]

        self.gtree = GapTree(tb_bbox)  # 算法对象

    def run(self, textBlocks):
        textBlocks = linePreprocessing(textBlocks)  # 预处理
        textBlocks = self.gtree.sort(textBlocks)  # 构建间隙树
        # 补充行尾间隔符
        for tb in textBlocks:
            tb["end"] = "\n"
            del tb["normalized_bbox"]
        return textBlocks
