# 段落分析器
# 对已经是一个列区块之内的文本块，判断其段落关系。

from typing import Callable
import unicodedata


# 传入前句尾字符和后句首字符，返回分隔符
def word_separator(letter1, letter2):

    # 判断Unicode字符是否属于中文、日文或韩文字符集
    def is_cjk(character):
        cjk_unicode_ranges = [
            (0x4E00, 0x9FFF),  # 中文
            (0x3040, 0x30FF),  # 日文
            (0x1100, 0x11FF),  # 韩文
            (0x3130, 0x318F),  # 韩文兼容字母
            (0xAC00, 0xD7AF),  # 韩文音节
            # 全角符号
            (0x3000, 0x303F),  # 中文符号和标点
            (0xFE30, 0xFE4F),  # 中文兼容形式标点
            (0xFF00, 0xFFEF),  # 半角和全角形式字符
        ]
        return any(start <= ord(character) <= end for start, end in cjk_unicode_ranges)

    if is_cjk(letter1) and is_cjk(letter2):
        return ""

    # 特殊情况：前文为连字符。
    if letter1 == "-":
        return ""
    # 特殊情况：后文为任意标点符号。
    if unicodedata.category(letter2).startswith("P"):
        return ""
    # 其它正常情况加空格
    return " "


TH = 1.2  # 行高用作对比的阈值


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

    # 执行分析
    def _parse(self, units):
        units.sort(key=lambda a: a[0][1])  # 确保从上到下有序
        para_l, para_top, para_r, para_bottom = units[0][0]  # 当前段的左右
        para_line_h = para_bottom - para_top  # 当前段行高
        para_line_s = None  # 当前段行间距
        now_para = [units[0]]  # 当前段的块
        paras = []  # 总的段
        paras_line_space = []  # 总的段的行间距
        # 取 左右相等为一个自然段的主体
        for i in range(1, len(units)):
            l, top, r, bottom = units[i][0]  # 当前块上下左右边缘
            h = bottom - top
            ls = top - para_bottom  # 行间距
            # 检测是否同一段
            if (  # 左右边缘都相等
                abs(para_l - l) <= para_line_h * TH
                and abs(para_r - r) <= para_line_h * TH
                # 行间距不大
                and (para_line_s == None or ls < para_line_s + para_line_h * 0.5)
            ):
                # 更新数据
                para_l = (para_l + l) / 2
                para_r = (para_r + r) / 2
                para_line_h = (para_line_h + h) / 2
                para_line_s = ls if para_line_s == None else (para_line_s + ls) / 2
                # 添加到当前段
                now_para.append(units[i])
            else:  # 非同一段，归档上一段，创建新一段
                paras.append(now_para)
                paras_line_space.append(para_line_s)
                now_para = [units[i]]
                para_l, para_r, para_line_h = l, r, bottom - top
                para_line_s = None
            para_bottom = bottom
        # 归档最后一段
        paras.append(now_para)
        paras_line_space.append(para_line_s)

        # 合并只有1行的段，添加到上/下段作为首/尾句
        for i1 in reversed(range(len(paras))):
            para = paras[i1]
            if len(para) == 1:
                l, top, r, bottom = para[0][0]
                up_flag = down_flag = False
                # 上段末尾条件：左对齐，右不超，行间距够小
                if i1 > 0:
                    # 检查左右
                    up_l, up_top, up_r, up_bottom = paras[i1 - 1][-1][0]
                    up_dist, up_h = abs(up_l - l), up_bottom - up_top
                    up_flag = up_dist <= up_h * TH and r <= up_r + up_h * TH
                    # 检查行间距
                    if (
                        paras_line_space[i1 - 1] != None
                        and top - up_bottom > paras_line_space[i1 - 1] + up_h * 0.5
                    ):
                        up_flag = False
                # 下段开头条件：右对齐/单行超出，左缩进
                if i1 < len(paras) - 1:
                    down_l, down_top, down_r, down_bottom = paras[i1 + 1][0][0]
                    down_h = down_bottom - down_top
                    # 左对齐或缩进
                    if down_l - down_h * TH <= l <= down_l + down_h * (1 + TH):
                        if len(paras[i1 + 1]) > 1:  # 多行，右对齐
                            down_flag = abs(down_r - r) <= down_h * TH
                        else:  # 单行，右可超出
                            down_flag = down_r - down_h * TH < r
                    # 检查行间距
                    if (
                        paras_line_space[i1 + 1] != None
                        and down_top - bottom > paras_line_space[i1 + 1] + down_h * 0.5
                    ):
                        down_flag = False

                # 选择添加到上还是下段
                if up_flag and down_flag:  # 两段都符合，则选择垂直距离更近的
                    if top - up_bottom < down_top - bottom:
                        paras[i1 - 1].append(para[0])
                    else:
                        paras[i1 + 1].insert(0, para[0])
                elif up_flag:  # 只有一段符合，直接选择
                    paras[i1 - 1].append(para[0])
                elif down_flag:
                    paras[i1 + 1].insert(0, para[0])
                if up_flag or down_flag:
                    del paras[i1]
                    del paras_line_space[i1]

        # 刷新所有段，添加end
        for para in paras:
            for i1 in range(len(para) - 1):
                letter1 = para[i1][1][1]  # 行1结尾字母
                letter2 = para[i1 + 1][1][0]  # 行2开头字母
                sep = word_separator(letter1, letter2)
                self.set_end(para[i1][2], sep)
            self.set_end(para[-1][2], "\n")
        return units
