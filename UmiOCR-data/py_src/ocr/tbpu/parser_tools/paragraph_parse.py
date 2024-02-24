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
        para_l, top, para_r, bottom = units[0][0]  # 当前段的左右
        para_line_h = bottom - top  # 当前段行高
        now_para = [units[0]]  # 当前段的块
        paras = []  # 总的段
        # 取 左右相等为一个自然段的主体
        for i in range(1, len(units)):
            l, top, r, bottom = units[i][0]  # 当前块上下左右边缘
            h = bottom - top
            # 左右边缘都相等，为同一段
            if abs(para_l - l) <= para_line_h and abs(para_r - r) <= para_line_h:
                # 更新数据
                para_l = (para_l + l) / 2
                para_r = (para_r + r) / 2
                para_line_h = (para_line_h + h) / 2
                # 添加到当前段
                now_para.append(units[i])
            else:  # 非同一段，归档上一段，创建新一段
                paras.append(now_para)
                now_para = [units[i]]
                para_l, para_r = l, r
                para_line_h = bottom - top
        # 归档最后一段
        paras.append(now_para)

        # 合并只有1行的段，添加到上/下段作为首/尾句
        # TODO: 精简逻辑
        for i1 in reversed(range(len(paras))):
            para = paras[i1]
            if len(para) == 1:
                l, top, r, bottom = para[0][0]
                flag_l = False
                # 检查作为上一段结尾的可行性
                if i1 > 0:
                    i2 = i1 - 1
                    para_l, top, para_r, bottom = paras[i2][-1][0]
                    para_line_h = bottom - top
                    if abs(para_l - l) <= para_line_h:
                        flag_l = True
                # 检查作为下一段开头的可行性
                if i1 < len(paras) - 1:
                    i2 = i1 + 1
                    para_l, top, para_r, bottom = paras[i2][0][0]
                    para_line_h = bottom - top
                    if abs(para_r - r) <= para_line_h:
                        # 两头都匹配，取最小值
                        if flag_l and abs(para_l - l) < abs(para_r - r):
                            paras[i2].append(para[0])
                            del paras[i1]
                            continue
                        else:
                            paras[i2].insert(0, para[0])
                            del paras[i1]
                            continue
                if flag_l:
                    i2 = i1 - 1
                    paras[i2].append(para[0])
                    del paras[i1]
                    continue
        # 刷新所有段，添加end
        for para in paras:
            for i1 in range(len(para) - 1):
                i2 = i1 + 1
                sep = self._word_separator(para[i1], para[i2])
                self.set_end(para[i1][2], sep)
            self.set_end(para[-1][2], "\n")
        return units
