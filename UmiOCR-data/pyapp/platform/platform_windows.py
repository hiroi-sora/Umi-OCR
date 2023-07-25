# ==============================================
# =============== Windows系统API ===============
# ==============================================

from .platform import PlatformBase

import os

class PlatformWindows(PlatformBase):

    @staticmethod
    def shutdown():  # 关机
        os.system("shutdown /s /t 0")

    @staticmethod
    def hibernate():  # 休眠
        os.system("shutdown /h")