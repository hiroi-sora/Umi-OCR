# 排版解析-不做处理

from .tbpu import Tbpu


class ParserNone(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-不做处理"

    def run(self, textBlocks):
        for tb in textBlocks:
            if "end" not in tb:
                tb["end"] = "\n"  # 默认结尾间隔符为换行
        return textBlocks
