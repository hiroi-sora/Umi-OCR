# 输出器的基类。按指定的格式，将传入的文本输出到指定地方。

from utils.logger import GetLog
Log = GetLog()


class Output:

    def print(self, text):
        '''直接输出文字'''
        Log.info(f'输出: {text}')
