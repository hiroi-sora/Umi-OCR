# 文块处理：合并横排多行
from ocr.tbpu.merge_line_h import TbpuLineH

from time import time


class TbpuLineHMulti(TbpuLineH):

    def getInitInfo(self):
        return '文块后处理：[横排多行合并]'

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
            bx, by = box[3][0], box[3][1]  # 左下角xy
            bh = box[3][1] - box[0][1]  # 行高
            limitX, limitY = bh, bh*2  # x、y 合并阈值，行高、行高两倍（最多两倍行间距）
            num = 1  # 合并个数
            # 遍历后续文块
            for i in range(index+1, listlen):
                tb2 = hList[i]
                if not tb2:
                    continue
                box2 = tb2['box']
                b2x, b2y = box2[0][0], box2[0][1]  # 左上角xy
                b2h = box2[3][1] - box2[0][1]  # 行高
                # 文块1的左下角与文块2的左上角接壤，且二者行高一致，则合并
                if abs(b2x-bx) < limitX and abs(b2y-by) < limitY and abs(b2h-bh) < limitY:
                    num += 1
                    # 合并两个文块box
                    xMin = min(box[0][0], box[3][0], box2[0][0], box2[3][0])
                    xMax = max(box[1][0], box[2][0], box2[1][0], box2[2][0])
                    box[0][0] = box[3][0] = xMin  # x左
                    box[1][0] = box[2][0] = xMax  # x右
                    box[0][1] = box[1][1] = min(box[0][1], box[1][1])  # y上
                    box[2][1] = box[3][1] = max(box2[2][1], box2[3][1])  # y下
                    # 刷新临时变量（行高与阈值不变）
                    bx, by = box[3][0], box[3][1]  # 左下角xy
                    # 合并内容
                    tb['score'] += tb2['score']  # 合并置信度
                    tb['text'] += tb2['text']  # 合并文本
                    hList[i] = None  # 置为空，标记删除
            if num > 1:
                tb['score'] /= num  # 平均置信度
            resList.append(tb)  # 装填入结果
        # 返回新文块组和debug字符串
        return resList, f'[横排多行合并] 原{len(textBlocks)}块，合并后{len(resList)}块，耗时{time()-timeIn}s'
