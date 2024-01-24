# 排版解析-多栏-自然段

from .tbpu import Tbpu
from .gap_tree import GapTree  # 间隙树排序算法
from .paragraph_parse import ParagraphParse  # 段内分析器


class MultiPara(Tbpu):
    def __init__(self):
        self.tbpuName = "排版解析-多栏-自然段"

        def tb_bbox(tb):  # 从文本块对象中，提取左上角、右下角坐标元组
            b = tb["box"]
            return (b[0][0], b[0][1], b[2][0], b[2][1])

        self.gtree = GapTree(tb_bbox)  # 算法对象

        def get_info(tb):  # 返回信息
            b = tb["box"]
            return ((b[0][0], b[0][1], b[2][0], b[2][1]), tb["text"])

        def set_end(tb, end):  # 获取预测的块尾分隔符
            tb["end"] = end

        self.pp = ParagraphParse(get_info, set_end)  # 段内分析器

    def run(self, textBlocks):
        textBlocks = self.gtree.sort(textBlocks)  # 构建间隙树
        nodes = self.gtree.get_nodes_text_blocks()  # 获取树节点序列
        # 段内分析
        for tbs in nodes:
            self.pp.run(tbs)  # 预测结尾分隔符
        return textBlocks
