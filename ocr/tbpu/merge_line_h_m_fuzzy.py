# 文块处理：横排-合并多行-模糊匹配
from ocr.tbpu.merge_line_h_m_left import TbpuLineHMultiLeft


class TbpuLineHMultiFuzzy(TbpuLineHMultiLeft):
    def __init__(self):
        super().__init__()
        self.tbpuName = '横排-合并多行-模糊匹配'

    def isRuleMerge(self, box1, box2):
        '''合并规则：两个box可以合并时返回T'''
        # 1与2在x上互相包含，y上接壤时OK
        return self.isBoxInX(box1, box2) and abs(box2[0][1]-box1[3][1]) <= self.limitY

    def isRuleNew(self, box1, box2):
        '''新段规则：两个box属于同一栏但不同段落时返回T'''
        # 无需判断
        return False
