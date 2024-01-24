# tbpu : text block processing unit
# 文块处理器的基类。
# OCR返回的结果中，一项包含文字、包围盒、置信度的元素，称为一个“文块” - text block 。
# 文块不一定是完整的一句话或一个段落。反之，一般是零散的文字。
# 一个OCR结果常由多个文块组成。
# 文块处理器就是：将传入的多个文块进行处理，比如合并、排序、删除文块。


class Tbpu:
    def __init__(self):
        self.tbpuName = "文块处理单元-未知"

    def run(self, textBlocks):
        """输入：textBlocks文块列表\n
        输出：排序后的textBlocks文块列表，每个块增加键：
        'end' 结尾间隔符
        """
        return textBlocks
