from .merge_line import MergeLine
from .merge_para import MergePara
from .merge_line_v_lr import MergeLineVlr
from .merge_line_v_rl import MergeLineVrl


Merge = {
    "MergeLine": MergeLine,
    "MergePara": MergePara,
    "MergeLineVlr": MergeLineVlr,
    "MergeLineVrl": MergeLineVrl,
}
