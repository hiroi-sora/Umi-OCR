# proc == processing
# 文块处理器的基类。
# OCR返回的结果中，一项包含文字、包围盒、置信度的元素，称为一个“文块” - text block 。
# 文块不一定是完整的一句话或一个段落。反之，一般是零散的文字。
# 一个OCR结果常由多个文块组成。
# 文块处理器就是：将传入的多个文块进行处理，比如合并、排序、删除文块。

from utils.logger import GetLog
Log = GetLog()


class Proc:

    def getInitInfo(self):
        return '未知文块处理器\n'

    def run(self, textBlocks, img):
        '''textBlocks文块，img图片信息'''
        Log.info(f'f: {textBlocks}')
        return textBlocks, '未知文块处理器'
