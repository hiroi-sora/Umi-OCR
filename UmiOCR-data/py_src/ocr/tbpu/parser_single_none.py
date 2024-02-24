# 排版解析-单栏-无换行

from .parser_single_line import SingleLine
from .parser_tools.paragraph_parse import word_separator  # 上下句间隔符


class SingleNone(SingleLine):
    def __init__(self):
        self.tbpuName = "排版解析-单栏-无换行"

    def run(self, textBlocks):
        textBlocks = super().run(textBlocks)
        # 找到换行符，更改为间隔符
        for i in range(len(textBlocks) - 1):
            if textBlocks[i]["end"] == "\n":
                letter1 = textBlocks[i]["text"][-1]
                letter2 = textBlocks[i + 1]["text"][0]
                textBlocks[i]["end"] = word_separator(letter1, letter2)
        return textBlocks
