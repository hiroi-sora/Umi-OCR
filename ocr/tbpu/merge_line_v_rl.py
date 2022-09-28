# 文块处理：合并竖排单行-从右至左
from ocr.tbpu.merge_line_v_lr import TbpuLineVlr

from time import time


class TbpuLineVrl(TbpuLineVlr):
    def __init__(self):
        self.tbpuName = '竖排-从右到左-单行'
        self.rl = True  # T为从右到左，F为从左到右

    def getInitInfo(self):
        return f'文块后处理：[{self.tbpuName}]'

    def run(self, textBlocks, imgInfo):
        '''传入 文块组、图片信息。返回文块组、debug信息字符串。'''
        timeIn = time()
        resList, s = super().run(textBlocks, imgInfo)
        # 返回新文块组和debug字符串
        return resList, f'[{self.tbpuName}] 原{len(textBlocks)}块，合并后{len(resList)}块，耗时{time()-timeIn}s'
