# 排版解析-多栏-自然段

from .tbpu import Tbpu


class MultiPara(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-多栏-自然段"

    def run(self, textBlocks):
        """输入：textBlocks文块列表\n
        输出：排序后的textBlocks文块列表，每个块增加键：
        'end' 结尾间隔符
        """
        return textBlocks
