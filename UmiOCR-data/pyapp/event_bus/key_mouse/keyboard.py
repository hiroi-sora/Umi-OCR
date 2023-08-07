from pynput import keyboard

from ...platform import Platform


# 按键转换器
class KeyTranslator:
    # 回调函数的 KeyCode 类型 转为键名字符串
    @staticmethod
    def key2name(key):
        return Platform.getKeyName(key)

    # 键名字符串 转为KeyCode
    @staticmethod
    def name2key(char):
        if hasattr(keyboard.Key, char):  # 控制键返回Code
            return getattr(keyboard.Key, char).value
        else:  # 非控制键返回自己
            return char


# 热键控制器类
class HotkeyController:
    def __init__(self):
        self.listener = None  # 监听器
        self.__start()

    # ========================= 【接口】 =========================

    # ========================= 【实现】 =========================

    # 第一次注册热键时，启动监听
    def __start(self):
        if not self.listener:
            self.listener = keyboard.Listener(
                on_press=self.__onPress, on_release=self.__onRelease
            )
            self.listener.start()

    # 按键按下的回调
    def __onPress(self, key):
        key = KeyTranslator.key2name(key)
        print(f"按下 {key}")

    # 按键抬起的回调
    def __onRelease(self, key):
        key = KeyTranslator.key2name(key)
        # print(f"松开 {key}")
