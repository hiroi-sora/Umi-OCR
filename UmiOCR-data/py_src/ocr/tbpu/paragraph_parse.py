# 段落分析器
# 对已经是一个列区块之内的文本块，判断其段落关系。

from typing import Callable
import re


class ParagraphParse:
    def __init__(self, get_info: Callable, set_end: Callable) -> None:
        """
        :param get_info: 函数，传入单个文本块，
                返回该文本块的信息元组： ( (x0, y0, x1, y1), "文本" )
        :param set_end: 函数，传入单个文本块 和文本尾部的分隔符，该函数要将分隔符保存。
        """
        self.get_info = get_info
        self.set_end = set_end

    # ======================= 调用接口：对文本块列表进行结尾分隔符预测 =====================
    def run(self, text_blocks: list):
        """
        对属于一个区块内的文本块列表，进行段落分析，预测每个文本块结尾的分隔符。

        :param text_blocks: 文本块对象列表
        :return: 排序后的文本块列表
        """
        # 封装块单元
        units = self._get_units(text_blocks, self.get_info)
        # 执行分析
        self._parse(units)
        return text_blocks

    # ======================= 封装块单元列表 =====================
    # 将原始文本块，封装为 ( (x0,y0,x2,y2), ("开头","结尾"), 原始 ) 。
    def _get_units(self, text_blocks, get_info):
        units = []
        for tb in text_blocks:
            bbox, text = get_info(tb)
            units.append((bbox, (text[0], text[-1]), tb))
        return units

    # ======================= 分析 =====================

    # 获取两个连续的行的单词分隔符
    def _word_separator(self, unit1, unit2):
        letter1 = unit1[1][1]  # 行1结尾字母
        letter2 = unit2[1][0]  # 行2开头字母

        # 判断结尾和开头，是否属于汉藏语族
        # 汉藏语族：行间无需分割符。印欧语族：则两行之间需加空格。
        ranges = [
            (0x4E00, 0x9FFF),  # 汉字
            (0x3040, 0x30FF),  # 日文
            (0xAC00, 0xD7AF),  # 韩文
            (0xFF01, 0xFF5E),  # 全角字符
        ]
        fa, fb = False, False
        for l, r in ranges:
            if l <= ord(letter1) <= r:
                fa = True
            if l <= ord(letter2) <= r:
                fb = True
        if fa and fb:
            return ""

        # 特殊情况：字母2为缩写，如 n't。或者字母2为结尾符号，意味着OCR错误分割。
        if letter2 in {r"'", ",", ".", "!", "?", ";", ":"}:
            return ""
        # 其它正常情况加空格
        return " "

    # 执行分析
    def _parse(self, units):
        units.sort(key=lambda a: a[0][1])  # 确保从上到下有序
        for i1 in range(len(units) - 1):
            i2 = i1 + 1  # i1为当前行，i2为下一行
            l1, top1, r1, bottom1 = units[i1][0]  # 上下左右边缘
            h1 = bottom1 - top1  # 行高
            l2, top2, r2, bottom2 = units[i2][0]
            h2 = bottom2 - top2
            hp = (h1 + h2) * 0.5  # 平均行高
            # 若垂直距离大于2倍行高，则为下一段
            # TODO: 计算平均行间距，大于平均的是换段。
            if top2 > bottom1 + hp * 2:
                self.set_end(units[i1][2], "\n")
                continue
            # 行1的左边缘接近行2，或行1缩进2格，则两行可能在同一段内
            if l1 - 3 * hp <= l2 <= l1 + hp:
                # 行1右边缘内缩，则不是同一段
                if r1 < r2 - hp * 2:
                    self.set_end(units[i1][2], "\n")
                    continue
                else:
                    sep = self._word_separator(units[i1], units[i2])
                    self.set_end(units[i1][2], sep)
                    continue
            self.set_end(units[i1][2], "\n")
        # 区块末加上换行
        self.set_end(units[-1][2], "\n")
        return units
