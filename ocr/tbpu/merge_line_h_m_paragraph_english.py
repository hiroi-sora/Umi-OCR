# 文块处理：横排-合并多行-英文自然段
from ocr.tbpu.merge_line_h_m_paragraph import TbpuLineHMultiParagraph


class TbpuLineHMultiParagraphEnglish(TbpuLineHMultiParagraph):
    def __init__(self):
        super().__init__()
        self.tbpuName = '横排-合并多行-英文自然段'

    def merge2text(self, text1, text2):
        '''合并两段文字的规则'''
        return text1 + ' ' + text2
