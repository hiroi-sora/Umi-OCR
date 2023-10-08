# 负责 pynput 的按键转换
# 封装 keyTranslator ，负责key、char、vk的转换

from pynput._util.win32 import KeyTranslator


# ==================== 按键转换器 ====================
# 封装 keyTranslator ，负责key、char、vk的转换
class _KeyTranslatorApi:
    def __init__(self):
        self._kt = KeyTranslator()
        self._layout, _layoutData = self._kt._generate_layout()
        self._normalLayout = _layoutData[(False, False, False)]  # 选取常规布局，不受修饰键影响

    def __call__(self, key):
        """传入pynput的Key对象，返回与修饰键无关的键名char"""
        # 比如，就算按下Shift再按“=”，依然返回“=”而不是“+”
        try:
            if hasattr(key, "name"):  # 若为控制键
                name = key.name.replace("cmd", "win")  # win键名称修正
                if "_" in name:  # 清除 _l _r 标记后缀
                    name = name.split("_", 1)[0].lower()
                return name.lower()
            else:  # 若为非控制键，通过vk获取键名，避免组合键的char为空
                scan = self._kt._to_scan(key.vk, self._layout)  # vk转扫描码
                char = self._normalLayout[scan][0]  # 扫描码转char
                return char.lower()
        except Exception as e:  # 特殊键（如Fn）没有对应字符，会跳到这里
            if key and hasattr(key, "vk"):
                return f"<{key.vk}>"  # 未知键值，无对应字符，返回键值本身
            else:
                print(f"[Error] 键值转换异常，未知键值！{str(key)} {type(key)}")
                return str(key)


_KTA = _KeyTranslatorApi()


def getKeyName(key):  # 键值转键名
    return _KTA(key)
