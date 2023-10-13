# =========================================
# =============== 主题连接器 ===============
# =========================================

from PySide2.QtCore import QObject, Slot, Signal

ThemePath = "themes.json"


class ThemeConnector(QObject):
    # 读取主题
    @Slot(result=str)
    def loadThemeStr(self):
        try:
            with open(ThemePath, "r", encoding="utf-8") as f:
                r = f.read()
                return r
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[Warning] 读取主题文件失败：{e}")
        return ""

    # 保存主题
    @Slot(str)
    def saveThemeStr(self, tstr):
        try:
            with open(ThemePath, "w", encoding="utf-8") as f:
                f.write(tstr)
        except Exception as e:
            print(f"[Warning] 写入主题文件失败：{e}")
