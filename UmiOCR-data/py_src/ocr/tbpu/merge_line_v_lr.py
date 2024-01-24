# 合并：单行-竖排-从左到右

from .tbpu import Tbpu


class MergeLineVlr(Tbpu):
    def __init__(self):
        super().__init__()
        self.tbpuName = "单行-竖排-从左到右"
        self.rl = False  # T为从右到左，F为从左到右

    def run(self, textBlocks):
        """传入 文块组、图片信息。返回文块组、debug信息字符串。"""
        # 所有文块，按左上角点的y坐标排序
        textBlocks.sort(key=lambda tb: tb["box"][0][1])
        # 遍历每个文块，寻找后续文块中与它接壤、且行宽一致的项，合并两个文块
        resList = []
        listlen = len(textBlocks)
        for index in range(listlen):
            tb = textBlocks[index]
            if not tb:
                continue
            box = tb["box"]
            bx, by = box[2][0], box[2][1]  # 右下角xy
            bw = box[1][0] - box[0][0]  # 行宽
            limitX, limitY = round(bw / 2), bw  # x、y 合并阈值，行宽一半、行宽
            num = 1  # 合并个数
            # 遍历后续文块
            for i in range(index + 1, listlen):
                tb2 = textBlocks[i]
                if not tb2:
                    continue
                box2 = tb2["box"]
                b2x, b2y = box2[1][0], box2[1][1]  # 右上角xy
                b2w = box2[1][0] - box2[0][0]  # 行宽
                # 文块1的右下角与文块2的右上角接壤，且二者行宽一致，则合并
                if (
                    abs(b2x - bx) < limitX
                    and abs(b2y - by) < limitY
                    and abs(b2w - bw) < limitY
                ):
                    num += 1
                    # 合并两个文块box
                    xMin = min(box[0][0], box[3][0], box2[0][0], box2[3][0])
                    xMax = max(box[1][0], box[2][0], box2[1][0], box2[2][0])
                    box[0][0] = box[3][0] = xMin  # x左
                    box[1][0] = box[2][0] = xMax  # x右
                    box[0][1] = box[1][1] = min(box[0][1], box[1][1])  # y上
                    box[2][1] = box[3][1] = max(box2[2][1], box2[3][1])  # y下
                    # 刷新临时变量
                    bx, by = box[2][0], box[2][1]  # 右下角xy
                    bw = box[1][0] - box[0][0]  # 行宽
                    limitX, limitY = round(bw / 2), bw  # x、y 合并阈值，行宽一半、行宽
                    # 合并内容
                    tb["score"] += tb2["score"]  # 合并置信度
                    tb["text"] += tb2["text"]  # 合并文本
                    textBlocks[i] = None  # 置为空，标记删除
            if num > 1:
                tb["score"] /= num  # 平均置信度
            resList.append(tb)  # 装填入结果
        # 所有新文块，按左上角点的x坐标从左到右排序
        resList.sort(key=lambda tb: tb["box"][0][0], reverse=self.rl)
        # 返回新文块组和debug字符串
        return resList
