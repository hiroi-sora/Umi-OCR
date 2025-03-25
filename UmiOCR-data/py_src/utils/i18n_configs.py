# UI语言设置

import os
from PySide2.QtCore import QTranslator

from . import pre_configs
from plugin_i18n import setLangCode
from umi_log import logger

I18nDir = "i18n"  # 翻译文件 目录
DefaultLang = "zh_CN"  # 默认语言，项目中qsTr()标记的原生语言，无翻译文件。

# 语言表。每个语种只有第一个语言代码是有效的（对应到翻译文件.qm），
# 其余的语言代码会映射到第一个。如zh_HK会映射到zh_TW，en_CA映射到en_US。
# https://www.science.co.il/language/Locale-codes.php
LanguageCodes = {
    # ===== 简中 =====
    "zh_CN": "简体中文",
    "zh": "简体中文",
    # ===== 繁中 =====
    "zh_TW": "繁體中文",  # 中国台湾
    "zh_HK": "繁體中文",  # 中国香港
    "zh_MO": "繁體中文",  # 中国澳门
    "zh_SG": "繁體中文",  # 新加坡
    # ===== 英语 =====
    "en_US": "English",  # 美国
    "en": "English",
    "en_GB": "English",  # 英国
    "en_AU": "English",  # 澳大利亚
    "en_CA": "English",  # 加拿大
    # ===== 日语 =====
    "ja_JP": "日本語",  # 日本
    # ===== 俄语 =====
    "ru_RU": "Русский",  # 俄罗斯
    "ru": "Русский",
    # ===== 葡萄牙语 =====
    "pt": "Português",
    "pt_BR": "Português",  # 巴西
    "pt_PT": "Português",  # 葡萄牙
    # ===== 泰米尔语 =====
    "ta": "தமிழ்",
    "ta_TA": "தமிழ்",
}

""" 暂未启用的语言
    # ===== 韩语 =====
    "ko_KR": "한국어",  # 韩国
    # ===== 法语 =====
    "fr_FR": "Français",  # 法国
    "fr": "Français",
    "fr_CA": "Français",  # 加拿大（魁北克）
    "fr_BE": "Français",  # 比利时
    # ===== 意大利语 =====
    "it_IT": "Italiano",
    # ===== 挪威语 =====
    "nb_NO": "norsk",
    # ===== 德语 =====
    "de_DE": "Deutsch",
    "de": "Deutsch",
    "de_AT": "Deutsch",
    "de_CH": "Deutsch",
    # ===== 西班牙语 Spanish =====
    "es_ES": "Español",
    "es_MX": "Español",
"""


class _I18n:
    def init(self, qtApp):
        translator = QTranslator()
        qtApp.translators = [translator]

        self.langCode = ""
        self.langDict = {}
        # 获取信息
        self._getLangPath()
        text, path = self.langDict[self.langCode]
        setLangCode(self.langCode)  # 设置插件翻译
        if not path:
            logger.debug("使用默认文本，未加载翻译。")
            return
        if not translator.load(path):
            msg = f"无法加载UI语言！\n[Error] Unable to load UI language: {path}"
            logger.warning(msg)
            os.MessageBox(msg, type_="warning")
            return
        if not qtApp.installTranslator(translator):  # 安装翻译器
            msg = f"无法加载翻译模块！\n[Error] Unable to installTranslator: {path}"
            logger.warning(msg)
            os.MessageBox(msg, type_="warning")
            return
        logger.info(f"i18n file loaded successfully. {self.langCode} - {text}")

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
                logger.warning(
                    f"The current system language is {code} and there is no corresponding i18n file. The default language used is {DefaultLang}."
                )


I18n = _I18n()
