import logging

LogName = 'Umi-OCR_log'
LogFileName = 'Umi-OCR_debug.log'


class Logger:

    def __init__(self):
        self.initLogger()

    def initLogger(self):
        '''初始化日志'''

        # 日志
        self.logger = logging.getLogger(LogName)
        self.logger.setLevel(logging.DEBUG)

        # 控制台
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logging.DEBUG)
        formatPrint = logging.Formatter(
            '【%(levelname)s】 %(message)s')
        streamHandler.setFormatter(formatPrint)
        # self.logger.addHandler(streamHandler)

        return
        # 日志文件
        fileHandler = logging.FileHandler(LogFileName)
        fileHandler.setLevel(logging.ERROR)
        formatFile = logging.Formatter(
            '''
【%(levelname)s】 %(asctime)s
%(message)s
    文件：%(module)s | 函数：%(funcName)s | 行号：%(lineno)d
    线程id：%(thread)d | 线程名：%(thread)s''')
        fileHandler.setFormatter(formatFile)
        self.logger.addHandler(fileHandler)


LOG = Logger()


def GetLog():
    return LOG.logger
