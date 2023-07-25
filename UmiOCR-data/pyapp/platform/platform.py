# ==========================================
# =============== 平台API基类 ===============
# ==========================================

class PlatformBase:

    @staticmethod
    def shutdown():  # 关机
        print("平台-关机")

    @staticmethod
    def hibernate():  # 休眠
        print("平台-休眠")