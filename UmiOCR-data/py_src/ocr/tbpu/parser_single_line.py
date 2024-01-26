# 排版解析-单栏-单行

from .tbpu import Tbpu
from .line_preprocessing import linePreprocessing  # 行预处理
from .paragraph_parse import ParagraphParse  # 段内分析器


class SingleLine(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-单栏-单行"

    def run(self, textBlocks):
        textBlocks = linePreprocessing(textBlocks)  # 预处理
        # 整版分析
        for tb in textBlocks:
            tb["end"] = "\n"
            del tb["normalized_bbox"]
        return textBlocks
