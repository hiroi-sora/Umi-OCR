# 排版解析-多栏-自然段

from .tbpu import Tbpu
from .parser_tools.line_preprocessing import linePreprocessing  # 行预处理
from .parser_tools.gap_tree import GapTree  # 间隙树排序算法
from .parser_tools.paragraph_parse import ParagraphParse  # 段内分析器


class MultiPara(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-多栏-自然段"

        # 间隙树对象
        self.gtree = GapTree(lambda tb: tb["normalized_bbox"])

        # 段内分析器对象
        get_info = lambda tb: (tb["normalized_bbox"], tb["text"])

        def set_end(tb, end):  # 获取预测的块尾分隔符
            tb["end"] = end

        self.pp = ParagraphParse(get_info, set_end)

    def run(self, textBlocks):
        textBlocks = linePreprocessing(textBlocks)  # 预处理
        textBlocks = self.gtree.sort(textBlocks)  # 构建间隙树
        nodes = self.gtree.get_nodes_text_blocks()  # 获取树节点序列
        # 对每个结点，进行自然段分析
        for tbs in nodes:
            self.pp.run(tbs)  # 预测结尾分隔符
            for tb in tbs:
                del tb["normalized_bbox"]
        return textBlocks
