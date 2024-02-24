# 排版解析-单栏-自然段

from .tbpu import Tbpu
from .parser_tools.line_preprocessing import linePreprocessing  # 行预处理
from .parser_tools.paragraph_parse import ParagraphParse  # 段内分析器


class SinglePara(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-单栏-自然段"

        # 段内分析器对象
        get_info = lambda tb: (tb["normalized_bbox"], tb["text"])

        def set_end(tb, end):  # 获取预测的块尾分隔符
            tb["end"] = end

        self.pp = ParagraphParse(get_info, set_end)

    def run(self, textBlocks):
        textBlocks = linePreprocessing(textBlocks)  # 预处理
        # 整版分析
        self.pp.run(textBlocks)  # 预测结尾分隔符
        for tb in textBlocks:
            del tb["normalized_bbox"]
        return textBlocks
