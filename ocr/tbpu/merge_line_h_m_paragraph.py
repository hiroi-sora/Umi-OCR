# 文块处理：横排-合并多行-自然段
from ocr.tbpu.merge_line_h_m_left import TbpuLineHMultiLeft


class TbpuLineHMultiParagraph(TbpuLineHMultiLeft):
    def __init__(self):
        super().__init__()
        self.tbpuName = '横排-合并多行-自然段'

    def isRuleMerge(self, box1, box2):
        '''合并规则：两个box可以合并时返回T'''
        # y不接壤，说啥也没用
        if abs(box2[0][1]-box1[3][1]) > self.limitY:
            return False
        # 若当前是第一行，则额外允许第二行的x位置前移最多2个全角字符（即行高）的距离
        if self.mergeNum == 1:
            # 第二行x额外允许的范围
            xMax = box1[3][0] + self.limitX  # 上界：第一行x
            xMin = box1[3][0] - self.rowHeight * \
                2.5 - self.limitX  # 下界：第一行x提前几个行高
            return xMin <= box2[0][0] <= xMax
        # 1的左下角与2的左上角接壤时OK
        return abs(box2[0][0]-box1[3][0]) <= self.limitX
