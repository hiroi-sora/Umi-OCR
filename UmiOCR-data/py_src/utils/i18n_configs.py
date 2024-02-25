# UI语言设置

import os
from . import pre_configs
from plugin_i18n import setLangCode

I18nDir = "i18n"  # 翻译文件 目录
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
        self._getLangPath()
        text, path = self.langDict[self.langCode]
        setLangCode(self.langCode)  # 设置插件翻译
        if not path:
            print("使用默认文本，未加载翻译。")
            return
        if not trans.load(path):
            msg = f"无法加载UI语言！\n[Error] Unable to load UI language: {path}"
            os.MessageBox(msg, type="warning")
            return
        if not qtApp.installTranslator(trans):  # 安装翻译器
            msg = f"无法加载翻译模块！\n[Error] Unable to installTranslator: {path}"
            os.MessageBox(msg, type="warning")
            return
        print(f"翻译加载完毕。{self.langCode} - {text}")

    # 切换语言
    def setLanguage(self, code):
        if code in self.langDict:
            self.langCode = code
            pre_configs.setValue("i18n", code)  # 写入预配置项
            return True
        return False

    # 获取语言参数
    def getInfos(self):
        return [self.langCode, self.langDict]

    # 获取当前翻译文件路径，如果没有配置文件则初始化
    def _getLangPath(self):
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
            text = LanguageCodes[DefaultLang]
            self.langDict[DefaultLang] = [text, ""]
        # 加载预配置项
        code = pre_configs.getValue("i18n")
        if code in self.langDict:
            self.langCode = code
        # 未能加载，则初始化预配置
        if not self.langCode:
            import locale

            # 取得当前系统语言
            code, encoding = locale.getdefaultlocale()
            # 映射首位代号
            if code in LanguageCodes:
                langStr = LanguageCodes[code]
                for c, l in LanguageCodes.items():
                    if l == langStr:
                        code = c
                        break
            # 尝试写入配置
            if not self.setLanguage(code):
                # 写入配置失败，则使用默认语言
                self.setLanguage(DefaultLang)
                print(
                    f"当前系统语言为{code}，无对应翻译文件，使用默认语言：{DefaultLang}。"
                )


I18n = _I18n()
