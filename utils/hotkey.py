from utils.pynput_hotkey import hotkeyApi
from utils.logger import GetLog


Log = GetLog()


class Hotkey():  # 热键

    # ========================== 键盘 ==============================

    @staticmethod
    def add(hotkey, callback):
        '''添加一个快捷键组合监听。按下时调用callback'''
        # suppress=False 允许按键事件继续向别的软件下发，否则系统中相同辅助键的快捷键全都失效
        hotkeyApi.add(hotkey, callback)
        Log.info(f'注册按下 ↓【{hotkey}】')

    @staticmethod
    def addRelease(hotkey, callback):
        '''添加一个快捷键组合监听。松开时调用callback'''
        hotkeyApi.addRelease(hotkey, callback)
        Log.info(f'注册抬起 ↑【{hotkey}】')

    @staticmethod
    def remove(hotkey):
        '''移除一个快捷键组合监听'''
        hotkeyApi.remove(hotkey)  # 移除该快捷键
        Log.info(f'注销监听 ×【{hotkey}】')

    @staticmethod
    def read(callback):
        '''录制快捷键。按下并松开一组按键，将按键序列字符串发送到回调函数\n
            成功：返回hotkey字符串\n
            失败：hotkey为空，errmsg为错误字符串'''
        hotkeyApi.read(callback)

    @staticmethod
    def isPressed(hotkey):
        '''检查当前是否按下hotkey序列，是返回T'''
        return hotkeyApi.isPressed(hotkey)

    @staticmethod
    def send(hotkey):
        '''发送按键序列'''
        hotkeyApi.send(hotkey)
        Log.info(f'发送按键组合【{hotkey}】')

    # ========================== 鼠标 ==============================

    @staticmethod
    def addMouseButtonDown(callback):
        '''添加一个鼠标按钮监听。按下时调用callback，返回xy坐标元组'''
        hotkeyApi.addMouseButtonDown(callback)

    @staticmethod
    def addMouseButtonUp(callback):
        '''添加一个鼠标按钮监听。松开时调用callback，返回xy坐标元组'''
        hotkeyApi.addMouseButtonUp(callback)

    @staticmethod
    def removeMouse():
        '''移除鼠标监听'''
        hotkeyApi.removeMouse()

    @staticmethod
    def getMousePos():
        '''获取鼠标当前位置'''
        return hotkeyApi.getMousePos()


"""
# 旧版热键类。依赖 keyboard 库，这个库年久失修Bug多，弃之。
# 顺带 mouse 也遗弃，pynput已经包含鼠标监听的接口。

import keyboard  # 绑定快捷键
import mouse  # 绑定鼠标键

class Hotkey():  
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

    # ========================== 鼠标1 ==============================

    @staticmethod
    def addMouseButtonDown(callback):
        '''添加一个鼠标按钮监听。按下时调用callback，返回xy坐标元组'''
        def cb():
            pos = mouse.get_position()  # 获取鼠标当前位置
            callback(pos)
        mouse.on_button(cb,
                        buttons=('left', 'right'), types='down')

    @staticmethod
    def addMouseButtonUp(callback):
        '''添加一个鼠标按钮监听。松开时调用callback，返回xy坐标元组'''
        def cb():
            pos = mouse.get_position()  # 获取鼠标当前位置
            callback(pos)
        mouse.on_button(cb,
                        buttons=('left', 'right'), types='up')

    @staticmethod
    def removeMouse():
        '''移除鼠标监听'''
        mouse.unhook_all()

    # ========================== 鼠标2 ==============================

    @staticmethod
    def addMouseButtonDown(callback):
        '''添加一个鼠标按钮监听。按下时调用callback，返回xy坐标元组'''
        hotkeyApi.addMouseButtonDown(callback)

    @staticmethod
    def addMouseButtonUp(callback):
        '''添加一个鼠标按钮监听。松开时调用callback，返回xy坐标元组'''
        hotkeyApi.addMouseButtonUp(callback)

    @staticmethod
    def removeMouse():
        '''移除鼠标监听'''
        hotkeyApi.removeMouse()
"""
