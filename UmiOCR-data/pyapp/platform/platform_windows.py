# ==============================================
# =============== Windows系统API ===============
# ==============================================

from pynput._util.win32 import KeyTranslator
import os
import re
import subprocess

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
    # 获取开始菜单路径。传值：user 用户菜单 | common 公共菜单
    @staticmethod
    def GetStartMenu(type="common"):
        if type == "user":
            return os.getenv("APPDATA") + "\\Microsoft\\Windows\\Start Menu"
        elif type == "common":
            return os.getenv("ProgramData") + "\\Microsoft\\Windows\\Start Menu"

    # 获取启动（开机自启）路径。
    @staticmethod
    def GetStartup(type="common"):
        return _StandardPaths.GetStartMenu(type) + "\\Programs\\Startup"


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

    @staticmethod
    def getUsedPorts():  # 获取系统中所有已占用的TCP端口号
        try:
            process = subprocess.Popen(
                "netstat -ano",
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                shell=True,
            )
            res, _ = process.communicate()
            res = str(res)
            lines = res.split(r"\n")
            ports = set()
            pattern = r":(\d+)\s"  # 冒号端口号空格
            for l in lines:
                if "TCP" in l:
                    match = re.search(pattern, l)
                    if match:
                        p = match.group(1)
                        ports.add(int(p))
            return ports
        except Exception as e:
            print(f"[Error] 获取占用端口号失败：{e}")
        return ()
