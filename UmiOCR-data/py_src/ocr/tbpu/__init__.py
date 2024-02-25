# tbpu : text block processing unit 文本块后处理

from .parser_none import ParserNone
from .ignore_area import IgnoreArea

from .parser_multi_para import MultiPara
from .parser_multi_line import MultiLine
from .parser_multi_none import MultiNone
from .parser_single_para import SinglePara
from .parser_single_line import SingleLine
from .parser_single_none import SingleNone
from .parser_single_code import SingleCode

# 排版解析
Parser = {
    "none": ParserNone,  # 不做处理
    "multi_para": MultiPara,  # 多栏-自然段
    "multi_line": MultiLine,  # 多栏-总是换行
    "multi_none": MultiNone,  # 多栏-无换行
    "single_para": SinglePara,  # 单栏-自然段
    "single_line": SingleLine,  # 单栏-总是换行
    "single_none": SingleNone,  # 单栏-无换行
    "single_code": SingleCode,  # 单栏-代码段
}


# 获取排版解析器对象
def getParser(key):
    if key in Parser:
        return Parser[key]()
    else:
        return Parser["none"]()
