# 合并：单行-竖排-从左到右

from .merge_line_v_lr import MergeLineVlr


class MergeLineVrl(MergeLineVlr):
    def __init__(self):
        super().__init__()
        self.tbpuName = "单行-竖排-从右到左"
        self.rl = True  # T为从右到左，F为从左到右
