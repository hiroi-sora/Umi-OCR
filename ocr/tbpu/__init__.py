# tbpu : text block processing unit
# 文本块处理单元

# OCR返回的结果中，一项包含文字、包围盒、置信度的元素，称为一个“文块” - text block 。
# 文块不一定是完整的一句话或一个段落。反之，一般是零散的文字。
# 一个OCR结果常由多个文块组成。
# 文块处理器就是：将传入的多个文块进行处理，比如合并、排序、删除文块。


# 概念解析：
# 栏：一页纸可能有单栏、双栏、多栏，不同栏之间的文本块不会接壤。不同栏的文块是绝对不能合并的。
# 段：一栏可能有多个段落，可能由行间距、起始空格等来区分。怎么划分段落、怎么合并，不同Tbpu有不同方案。
# 行：一段内可能有多个行。应该尽量合并。
# 块：文本块是OCR结果中的最小单位，一行可能被意外划分为多个块，这是不正常的，必须要合并。


from utils.config import Config
from ocr.tbpu.merge_line_h import TbpuLineH
from ocr.tbpu.merge_line_h_m_left import TbpuLineHMultiLeft
from ocr.tbpu.merge_line_h_m_paragraph import TbpuLineHMultiParagraph
from ocr.tbpu.merge_line_h_m_paragraph_english import TbpuLineHMultiParagraphEnglish
from ocr.tbpu.merge_line_h_m_fuzzy import TbpuLineHMultiFuzzy
from ocr.tbpu.merge_line_v_lr import TbpuLineVlr
from ocr.tbpu.merge_line_v_rl import TbpuLineVrl


Tbpus = {
    '优化单行': TbpuLineH,
    '合并多行-汉文自然段': TbpuLineHMultiParagraph,
    '合并多行-西文自然段': TbpuLineHMultiParagraphEnglish,
    '合并多行-左对齐': TbpuLineHMultiLeft,
    '合并多行-模糊匹配': TbpuLineHMultiFuzzy,
    '竖排-从左到右-单行': TbpuLineVlr,
    '竖排-从右至左-单行': TbpuLineVrl,
    '不做处理': None,
}

Config.set('tbpu', Tbpus)
