# 排版解析-单栏-单行

from .tbpu import Tbpu


class SingleLine(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-单栏-单行"

    def run(self, textBlocks):
        # 按y排序
        textBlocks.sort(key=lambda tb: tb["normalized_bbox"][1])
        # 补充换行
        for tb in textBlocks:
            tb["end"] = "\n"
        return textBlocks
