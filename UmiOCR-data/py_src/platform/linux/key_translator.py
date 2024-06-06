# 负责 pynput 的按键转换


def getKeyName(key):  # TODO: 键值转键名
    # 传入 pynput 按键事件对象，返回键名字符串
    if not isinstance(key, str):
        key = str(key)
    if not key:  # Error
        return ""
    if key.startswith("Key."):  # 修饰建
        key = key[4:]
    if key.startswith("'") and key.endswith("'"):
        key = key[1:-1]
    # print(f"获取键名:【{key}】")
    return key
