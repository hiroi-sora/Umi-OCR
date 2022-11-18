# 文块处理：横排-合并多行-左对齐
from ocr.tbpu.merge_line_h import TbpuLineH

from time import time


class TbpuLineHMultiLeft(TbpuLineH):
    def __init__(self):
        self.tbpuName = '横排-合并多行-左对齐'
        # x、y方向上合并的允许阈值，为该行的行高乘上比例因子
        self.factorX = 1
        self.factorY = 2
        # x、y方向上合并的允许阈值，像素。由行高与比例因子动态刷新。
        self.limitX = 10
        self.limitY = 10

        self.mergeNum = 1  # 当前合并段数
        self.rowHeight = 10  # 当前行高

    def getInitInfo(self):
        return f'文块后处理：[{self.tbpuName}]'

    @staticmethod
    def isBoxInX(box1, box2):
        '''两个box在x方向上互相包含时返回T'''
        return (box1[0][0] <= box2[0][0] <= box1[1][0])\
            or (box1[0][0] <= box2[1][0] <= box1[1][0])\
            or (box2[0][0] <= box1[0][0] <= box2[1][0])\
            or (box2[0][0] <= box1[1][0] <= box2[1][0])

    def isRuleMerge(self, box1, box2):
        '''合并规则：两个box可以合并时返回T'''
        # 1的左下角与2的左上角接壤时OK
        return abs(box2[0][0]-box1[3][0]) <= self.limitX\
            and abs(box2[0][1]-box1[3][1]) <= self.limitY

    def isRuleNew(self, box1, box2):
        '''新段规则：两个box属于同一栏但不同段落时返回T'''
        # 1与2互相包含时OK
        return self.isBoxInX(box1, box2)

    def merge2text(self, text1, text2):
        '''合并两段文字的规则'''
        return text1 + text2

    def run(self, textBlocks, imgInfo):
        '''传入 文块组、图片信息。返回文块组、debug信息字符串。'''
        timeIn = time()
        hList, s = super().run(textBlocks, imgInfo)  # 获取单行合并
        listlen = len(hList)
        resList = []
        # 遍历每个文块，寻找后续文块中x坐标相近、且行高一致的项，合并两个文块
        for index in range(listlen):
            tb = hList[index]
            if not tb:
                continue
            box = tb['box']
            self.rowHeight = box[3][1] - box[0][1]  # 行高
            # 该行的 x、y 合并阈值
            self.limitX = self.factorX * self.rowHeight
            self.limitY = self.factorY * self.rowHeight
            self.mergeNum = 1  # 合并个数
            # 遍历后续文块
            for i in range(index+1, listlen):
                tb2 = hList[i]
                if not tb2:
                    continue
                box2 = tb2['box']
                b2h = box2[3][1] - box2[0][1]  # 行高
                # 当行高一致，即有可能在同一栏内
                if abs(b2h-self.rowHeight) <= self.limitY:
                    # 符合合并规则，则合并
                    if self.isRuleMerge(box, box2):
                        self.mergeNum += 1
                        # 合并两个文块box
                        box[0][0] = box[3][0] = min(  # x左
                            box[0][0], box[3][0], box2[0][0], box2[3][0])
                        box[1][0] = box[2][0] = max(  # x右
                            box[1][0], box[2][0], box2[1][0], box2[2][0])
                        box[0][1] = box[1][1] = min(  # y上
                            box[0][1], box[1][1])
                        box[2][1] = box[3][1] = max(  # y下
                            box2[2][1], box2[3][1])
                        # 合并内容
                        tb['score'] += tb2['score']  # 合并置信度
                        # tb['text'] += tb2['text']  # 合并文本
                        tb['text'] = self.merge2text(  # 合并文本
                            tb['text'], tb2['text'])
                        hList[i] = None  # 置为空，标记删除
                    # 否则，若符合新段规则，则跳出对1的继续匹配
                    elif self.isRuleNew(box, box2):
                        break
            if self.mergeNum > 1:
                tb['score'] /= self.mergeNum  # 平均置信度
            resList.append(tb)  # 装填入结果
        # 返回新文块组和debug字符串
        return resList, f'[{self.tbpuName}] 原{len(textBlocks)}块，合并后{len(resList)}块，耗时{time()-timeIn}s'
