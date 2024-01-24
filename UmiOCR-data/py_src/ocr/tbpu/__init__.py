# tbpu : text block processing unit 文本块后处理

from .merge_line import MergeLine
from .merge_para import MergePara
from .merge_para_code import MergeParaCode
from .merge_line_v_lr import MergeLineVlr
from .merge_line_v_rl import MergeLineVrl
from .ignore_area import IgnoreArea


Merge = {
    "MergeLine": MergeLine,
    "MergePara": MergePara,
    "MergeParaCode": MergeParaCode,
    "MergeLineVlr": MergeLineVlr,
    "MergeLineVrl": MergeLineVrl,
}
