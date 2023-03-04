# 引擎内存优化
from utils.config import Config
from time import time


class OcrEngineRam:
    def __init__(self):
        self.lastTimer = 0  # 最后一个启动的计时器的时间戳

    def init(self, restart, getEngFlag, EngFlag):
        self.restart = restart
        self.getEngFlag = getEngFlag
        self.EngFlag = EngFlag

    def runBefore(self, ram):
        '''一次运行前'''
        ramMax = Config.get('ocrRamMaxFootprint')
        if ramMax > 0:
            if ram > ramMax:
                self.restart()

    def runAfter(self):
        '''一次运行后'''
        ramTimeMax = Config.get('ocrRamMaxTime')
        if ramTimeMax > 0:
            t = int(time() * 1000000)  # 定时器时间戳
            self.lastTimer = t
            Config.main.win.after(
                ramTimeMax*1000, lambda *e: self.runTimer(t))

    def runTimer(self, t):
        '''最后一次运行后，定时器生效'''
        if self.lastTimer == t and self.getEngFlag() == self.EngFlag.waiting:
            self.restart()


OcrEngRam = OcrEngineRam()
