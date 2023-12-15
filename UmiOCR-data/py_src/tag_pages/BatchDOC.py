# ========================================
# =============== 批量PDF页 ===============
# ========================================

from .page import Page  # 页基类
from ..mission.mission_doc import MissionDOC  # 任务管理器


class BatchDOC(Page):
    def __init__(self, *args):
        super().__init__(*args)
