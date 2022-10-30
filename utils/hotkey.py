from utils.logger import GetLog

import keyboard  # 绑定快捷键

Log = GetLog()


class Hotkey():  # 热键
    @staticmethod
    def add(hotkey, callback):
        '''添加一个快捷键组合监听。按下时调用callback'''
        # suppress=False 允许按键事件继续向别的软件下发，否则系统中相同辅助键的快捷键全都失效
        keyboard.add_hotkey(hotkey, callback, suppress=False)
        Log.info(f'注册按键按下【{hotkey}】')

    @staticmethod
    def addRelease(hotkey, callback):
        '''添加一个快捷键组合监听。松开时调用callback'''
        keyboard.on_release_key(hotkey, callback, suppress=False)
        Log.info(f'注册按键抬起【{hotkey}】')

    @staticmethod
    def remove(hotkey):
        '''移除一个快捷键组合监听'''
        keyboard.remove_hotkey(hotkey)  # 移除该快捷键
        Log.info(f'注销按键监听【{hotkey}】')

    @staticmethod
    def read(callback):
        '''录制快捷键。按下并松开一组按键，将按键序列字符串发送到回调函数\n
            成功：返回hotkey字符串\n
            失败：hotkey为空，errmsg为错误字符串'''
        try:
            hotkey = keyboard.read_hotkey(suppress=False)
            Log.info(f'录制按键组合【{hotkey}】')
            callback(hotkey)
        except ValueError as err:
            callback('', err)

    @staticmethod
    def isPressed(hotkey):
        '''检查当前是否按下hotkey序列，是返回T'''
        return keyboard.is_pressed(hotkey)

    @staticmethod
    def send(hotkey):
        '''发送按键序列'''
        keyboard.send(hotkey)
        Log.info(f'发送按键组合【{hotkey}】')
