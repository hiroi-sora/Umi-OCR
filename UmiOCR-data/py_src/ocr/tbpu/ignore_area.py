# 忽略区域

from .tbpu import Tbpu


class IgnoreArea(Tbpu):
    def __init__(self, areaList):
        self.tbpuName = "忽略区域"
        self.areaList = areaList

    def run(self, textBlocks):
        # 返回是否矩形框 a 包含 b
        def isInBox(a, b):
            return (
                a[0][0] <= b[0][0]
                and a[0][1] <= b[0][1]
                and a[2][0] >= b[2][0]
                and a[2][1] >= b[2][1]
            )

        newList = []
        for b in textBlocks:
            flag = True  # True 为没有被忽略
            # 检测当前文块 b 是否在任何一个检测块 a 内
            for a in self.areaList:
                if isInBox(a, b["box"]):
                    flag = False  # 踩到任何一个块，GG
                    break
            if flag:  # 没有被忽略
                newList.append(b)

        return newList
