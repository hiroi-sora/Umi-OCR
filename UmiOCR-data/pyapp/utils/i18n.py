# UI语言

import os
from PySide2.QtCore import QTranslator

I18nDir = "i18n"
I18nConfig = "_"
I18nConfig = os.path.join(I18nDir, I18nConfig)
DefaultLang = "zh_CN"
LanguageCodes = {
    "zh_CN": "简体中文",
    "zh_TW": "繁體中文",
    "zh_HK": "繁體中文",
    "en_US": "English",
    "en_GB": "English",
    "en_CA": "English",
    "es_ES": "Español",
    "es_MX": "Español",
    "fr_FR": "Français",
    "fr_CA": "Français",
    "de_DE": "Deutsch",
    "de_AT": "Deutsch",
    "de_CH": "Deutsch",
    "ja_JP": "日本語",
    "ko_KR": "한국어",
    "ru_RU": "Русский",
    "pt_BR": "Português",
    "pt_PT": "Português",
    "it_IT": "Italiano",
}


class _I18n:
    def init(self, qtApp, trans):
        # 获取信息
        self.__getLangPath()
        text, path = self.langDict[self.language]
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
        print(f"翻译加载完毕。{self.language} - {text}")

    # 切换语言
    def setLanguage(self, lang):
        if lang in self.langDict:
            with open(I18nConfig, "w", encoding="utf-8") as file:
                file.write(lang)
            return True
        return False

    # 获取语言参数
    def getInfos(self):
        return [self.language, self.langDict]

    # 获取当前翻译文件路径，如果没有配置文件则初始化
    def __getLangPath(self):
        self.langDict = {}
        self.language = ""
        for file in os.listdir(I18nDir):
            if file.endswith(".qm"):
                code = os.path.splitext(file)[0]
                path = os.path.join(I18nDir, file)
                text = LanguageCodes.get(code, code)
                self.langDict[code] = [text, path]
        if DefaultLang not in self.langDict:
            self.langDict[DefaultLang] = [LanguageCodes[DefaultLang], ""]
        print("qm列表：", self.langDict)

        # 存在配置文件
        if os.path.exists(I18nConfig):
            with open(I18nConfig, "r", encoding="utf-8") as file:
                text = file.read()
                if text in self.langDict:
                    self.language = text
        # 不存在，则初始化配置文件
        if not self.language:
            import locale

            l, encoding = locale.getdefaultlocale()
            if l in self.langDict:
                self.language = l
                with open(I18nConfig, "w", encoding="utf-8") as file:
                    file.write(l)
            else:
                self.language = DefaultLang
                print(f"当前系统语言为{l}，无对应翻译文件，使用默认语言：{DefaultLang}。")


I18n = _I18n()
