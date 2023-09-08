# UI语言

import os
from PySide2.QtCore import QTranslator

I18nDir = "i18n"
I18nConfig = "_"
I18nConfig = os.path.join(I18nDir, I18nConfig)


class _I18n:
    def init(self, qtApp, trans):
        # 获取信息
        self.language, self.qmDist = self.__getLangPath()
        if not self.language:
            print("翻译未加载。")
            return
        path = self.qmDist[self.language]
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
        print("翻译加载完毕。")

    # 获取当前翻译文件路径，如果没有配置文件则初始化
    def __getLangPath(self):
        qmDist = {}
        lang = ""
        for file in os.listdir(I18nDir):
            if file.endswith(".qm"):
                qmDist[os.path.splitext(file)[0]] = os.path.join(I18nDir, file)
        print("qm列表：", qmDist)

        # 存在配置文件
        if os.path.exists(I18nConfig):
            with open(I18nConfig, "r") as file:
                text = file.read()
                if text in qmDist:
                    lang = text
        # 不存在，则初始化配置文件
        else:
            import locale

            language, encoding = locale.getdefaultlocale()
            if language in qmDist:
                lang = language
                with open(I18nConfig, "w") as file:
                    file.write(lang)
            else:
                print(f"当前系统语言为{language}，无对应翻译文件。")

        return lang, qmDist


I18n = _I18n()
