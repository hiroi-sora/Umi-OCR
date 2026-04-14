# 负责 pynput 的按键转换
# macOS 平台实现：不依赖 win32 的 KeyTranslator

from umi_log import logger


# macOS 修饰键映射
_MODIFIER_MAP = {
    "cmd": "cmd",
    "cmd_l": "cmd",
    "cmd_r": "cmd",
    "alt": "option",
    "alt_l": "option",
    "alt_r": "option",
    "alt_gr": "option",
    "ctrl": "ctrl",
    "ctrl_l": "ctrl",
    "ctrl_r": "ctrl",
    "shift": "shift",
    "shift_l": "shift",
    "shift_r": "shift",
    "caps_lock": "caps_lock",
    "tab": "tab",
    "space": "space",
    "enter": "enter",
    "backspace": "backspace",
    "delete": "delete",
    "escape": "esc",
    "f1": "f1",
    "f2": "f2",
    "f3": "f3",
    "f4": "f4",
    "f5": "f5",
    "f6": "f6",
    "f7": "f7",
    "f8": "f8",
    "f9": "f9",
    "f10": "f10",
    "f11": "f11",
    "f12": "f12",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "home": "home",
    "end": "end",
    "page_up": "page_up",
    "page_down": "page_down",
}


def getKeyName(key):
    """传入pynput的Key对象，返回键名字符串"""
    try:
        if hasattr(key, "name"):  # 控制键（如 Key.cmd, Key.shift）
            name = key.name
            mapped = _MODIFIER_MAP.get(name)
            if mapped:
                return mapped
            # 去除 _l _r 标记后缀
            if "_" in name:
                name = name.split("_", 1)[0].lower()
            return name.lower()
        elif hasattr(key, "char") and key.char:  # 字符键
            return key.char.lower()
        elif hasattr(key, "vk") and key.vk is not None:  # 无字符但有虚拟键码
            return f"<{key.vk}>"
        else:
            return str(key)
    except Exception:
        logger.error(
            f"键值转换异常！key: {str(key)}, type: {type(key)}.",
            exc_info=True,
            stack_info=True,
        )
        return str(key)
