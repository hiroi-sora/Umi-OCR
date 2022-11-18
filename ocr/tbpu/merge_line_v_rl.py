# 文块处理：合并竖排单行-从右至左
from ocr.tbpu.merge_line_v_lr import TbpuLineVlr

from time import time


class TbpuLineVrl(TbpuLineVlr):
    def __init__(self):
        self.tbpuName = '竖排-从右到左-单行'
        self.rl = True  # T为从右到左，F为从左到右
