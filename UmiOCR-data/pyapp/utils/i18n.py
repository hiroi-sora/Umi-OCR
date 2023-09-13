# UI语言

import os
from PySide2.QtCore import QTranslator

I18nDir = "i18n"  # 翻译文件 目录
I18nConfig = "_"  # 配置文件名
I18nConfig = os.path.join(I18nDir, I18nConfig)
DefaultLang = "zh_CN"  # 默认语言
# 语言表。每个语种只有第一个代号是有效代号，剩下的会映射到第一个。如zh_HK会映射到zh_TW。
LanguageCodes = {
    "zh_CN": "简体中文",  # 简中
    "zh_TW": "繁體中文",  # 繁中
    "zh_HK": "繁體中文",
    "en_US": "English",  # 英语
    "en_GB": "English",
    "en_CA": "English",
    "es_ES": "Español",  # 西班牙语
    "es_MX": "Español",
    "fr_FR": "Français",  # 法语
    "fr_CA": "Français",
    "de_DE": "Deutsch",  # 德语
    "de_AT": "Deutsch",
    "de_CH": "Deutsch",
    "ja_JP": "日本語",  # 日语
    "ko_KR": "한국어",  # 韩语
    "ru_RU": "Русский",  # 俄语
    "pt_BR": "Português",  # 葡萄牙语
    "pt_PT": "Português",
    "it_IT": "Italiano",  # 意大利语
}


class _I18n:
    def init(self, qtApp, trans):
        self.langCode = ""
        self.langDict = {}
        # 获取信息
        self.__getLangPath()
        text, path = self.langDict[self.langCode]
        if not path:
            print("翻译未加载。")
            return
        if not trans.load(path):
            os.MessageBox(
                f"[Error] Unable to load UI language: {path}\n【异常】无法加载UI语言！",
                info="Umi-OCR Warning",
            )
            return
        if not qtApp.installTranslator(trans):  # 安装翻译器
            os.MessageBox(
                f"[Error] Unable to installTranslator: {path}\n【异常】无法加载翻译模块！",
                info="Umi-OCR Warning",
            )
            return
        print(f"翻译加载完毕。{self.langCode} - {text}")

    # 切换语言
    def setLanguage(self, lang):
        if lang in self.langDict:
            with open(I18nConfig, "w", encoding="utf-8") as file:
                file.write(lang)
            return True
        return False

    # 获取语言参数
    def getInfos(self):
        return [self.langCode, self.langDict]

    # 获取当前翻译文件路径，如果没有配置文件则初始化
    def __getLangPath(self):
        self.langDict = {}
        self.langCode = ""
        # 搜索本地翻译文件
        for file in os.listdir(I18nDir):
            if file.endswith(".qm"):
                code = os.path.splitext(file)[0]
                path = os.path.join(I18nDir, file)
                text = LanguageCodes.get(code, code)
                self.langDict[code] = [text, path]
        if DefaultLang not in self.langDict:
            self.langDict[DefaultLang] = [LanguageCodes[DefaultLang], ""]
        # 加载配置文件
        if os.path.exists(I18nConfig):
            with open(I18nConfig, "r", encoding="utf-8") as file:
                text = file.read()
                if text in self.langDict:
                    self.langCode = text
        # 不存在，则初始化配置文件
        if not self.langCode:
            import locale

            # 取得当前系统语言l
            code, encoding = locale.getdefaultlocale()
            # 映射首位代号
            if code in LanguageCodes:
                langStr = LanguageCodes[code]
                for c, l in LanguageCodes.items():
                    if l == langStr:
                        code = c
                        break
            # 检查是否存在对应翻译文件
            if code in self.langDict:
                self.langCode = code
                with open(I18nConfig, "w", encoding="utf-8") as file:
                    file.write(code)
            else:
                self.langCode = DefaultLang
                print(f"当前系统语言为{code}，无对应翻译文件，使用默认语言：{DefaultLang}。")


I18n = _I18n()
