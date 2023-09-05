# ==============================================
# =============== Windows系统API ===============
# ==============================================

from pynput._util.win32 import KeyTranslator
import os
import winreg  # 注册表

from .platform import PlatformBase


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


# ==================== 标准路径 ====================
# 获取系统的标准路径
class _StandardPaths:
    @property
    def StartMenu(self, type="user"):
        if type == "user":
            key = winreg.HKEY_CURRENT_USER
            name = "Start Menu"
        elif type == "common":
            key = winreg.HKEY_LOCAL_MACHINE
            name = "Common Start Menu"
        try:
            reg_key = winreg.OpenKey(
                key,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )
            start_menu_path = winreg.QueryValueEx(reg_key, name)[0]
            winreg.CloseKey(reg_key)
            return start_menu_path
        except Exception as e:
            print("[Error] 无法获取开始菜单路径。", e)
            return ""


_KTA = _KeyTranslatorApi()


# ==================== 对外接口 ====================
class PlatformWindows(PlatformBase):
    StandardPaths = _StandardPaths()

    @staticmethod
    def shutdown():  # 关机
        os.system("shutdown /s /t 0")

    @staticmethod
    def hibernate():  # 休眠
        os.system("shutdown /h")

    @staticmethod
    def getKeyName(key):  # 键值转键名
        return _KTA(key)
