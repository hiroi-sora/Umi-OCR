# 文块处理：忽略区域
from utils.config import Config
from ocr.tbpu.tbpu import Tbpu
from utils.logger import GetLog

from time import time

Log = GetLog()


class TbpuIgnoreArea(Tbpu):

    def __init__(self):
        self.areaInfo = Config.get('ignoreArea')  # 忽略区域信息

    def getInitInfo(self):
        return f'''文块后处理：[忽略区域]
适用分辨率：{self.areaInfo["size"]}
忽略区域A：{self.areaInfo["area"][0]}
识别区域：{self.areaInfo["area"][1]}
忽略区域B：{self.areaInfo["area"][2]}
'''

    def run(self, textBlocks, imgInfo):
        '''传入 文块组、图片信息。返回文块组、debug信息字符串。'''
        timeIn = time()
        # 尺寸不匹配，无需忽略区域
        if not self.areaInfo['size'][0] == imgInfo['size'][0] or not self.areaInfo['size'][1] == imgInfo['size'][1]:
            return textBlocks, f'[忽略区域] 图片尺寸为{self.areaInfo["size"][0]}x{self.areaInfo["size"][1]}，不符合忽略区域{imgInfo["size"][0]}x{imgInfo["size"][1]}'

        # 返回矩形框 bPos 是否在 aPos 内
        def isInBox(aPos0, aPos1, bPos0, bPos1):  # 检测框左上、右下角，待测者左上、右下角
            return bPos0[0] >= aPos0[0] and bPos0[1] >= aPos0[1] and bPos1[0] <= aPos1[0] and bPos1[1] <= aPos1[1]

        # 是否为忽略模式B
        def _isModeB_():
            if self.areaInfo['area'][1]:  # 需要检测
                for tb in textBlocks:  # 遍历每一个文字块
                    for a in self.areaInfo['area'][1]:  # 遍历每一个检测块
                        # 若任何一个文块 在 识别区域检测块内，返回true
                        if isInBox(a[0], a[1], (tb['box'][0][0], tb['box'][0][1]), (tb['box'][2][0], tb['box'][2][1])):
                            return True  # 跳出双循环
        isModeB = _isModeB_()
        modeIndex = 2 if isModeB else 0
        modeChar = 'B' if isModeB else 'A'
        fn = 0  # 记录忽略的数量
        tempList = []
        for tb in textBlocks:
            flag = True  # True 为没有被忽略
            # 检测当前文块 tb 是否在 modeIndex 模式的任何一个检测块内
            for a in self.areaInfo['area'][modeIndex]:
                if isInBox(a[0], a[1], (tb['box'][0][0], tb['box'][0][1]), (tb['box'][2][0], tb['box'][2][1])):
                    flag = False  # 踩到任何一个块，GG
                    break
            if flag:  # 没有被忽略
                tempList.append(tb)
            else:
                fn += 1
        # 返回新文块组和debug字符串
        return tempList, f'[忽略区域] 模式{modeChar}：忽略{fn}条，耗时{time()-timeIn}s'
