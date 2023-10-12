# =========================================
# =============== 主题提供器 ===============
# =========================================

# 用ini不用json，为了方便人修改

from configparser import ConfigParser

ThemePath = "themes.ini"

DefaultThemes = """
[Light]
themeTitle="明亮"
bgColor = "#FFF" # 背景
themeColor1 = "#FCF9BE" # 主题 背景
themeColor2 = "#FFDCA9" # 主题 装饰性前景
themeColor3 = "#C58940" # 主题 文字、图标
coverColor1 = "#11000000" # 叠加层 大部分需要突出的背景
coverColor2 = "#22000000" # 叠加层 按钮悬停
coverColor3 = "#33000000" # 叠加层 阴影
coverColor4 = "#55000000" # 叠加层 按钮按下
tabBarColor = "#F3F3F3" # 标签栏
textColor = "#000" # 主要文字
subTextColor = "#555" # 次要文字
yesColor = "#00CC00" # 允许、成功
noColor = "#FF0000" # 禁止、失败

[Dark]
themeTitle = "黑暗"
bgColor = "#444"
themeColor1 = "#005c99"
themeColor2 = "#009FFF"
themeColor3 = "#00BFFF"
coverColor1 = "#22FFFFFF"
coverColor2 = "#33FFFFFF"
coverColor3 = "#44FFFFFF"
coverColor4 = "#55FFFFFF"
tabBarColor = "#444"
textColor = "#FFF"
subTextColor = "#AAA"
yesColor = "#6EFC39"
noColor = "#FF2E2E"
"""


# 主题ini字符串转字典
def _themesStr2Dict(tstr):
    config = ConfigParser()
    config.read_string(tstr)
    tdict = {}
    for s in config.sections():
        tdict[s] = {}
        for option in config.options(s):
            tdict[s][option] = config.get(s, option)
    return tdict


# 获取主题
def getThemes():
    tdict = {}
    try:
        with open(ThemePath, "r", encoding="utf-8") as f:
            r = f.read()
            tdict = _themesStr2Dict(r)
    except Exception as e:
        print(f"[Warning] 读取主题失败，初始化默认主题。{e}")
        with open(ThemePath, "w", encoding="utf-8") as f:
            f.write(DefaultThemes)
        tdict = _themesStr2Dict(DefaultThemes)
    return tdict


# 设置主题
def setThemes(tdict):
    config = ConfigParser()
    try:
        for section, values in tdict.items():
            config[section] = values
        with open(ThemePath, "w") as file:
            config.write(file)
    except Exception as e:
        print(f"[Warning] 写入主题ini失败：{e}")
