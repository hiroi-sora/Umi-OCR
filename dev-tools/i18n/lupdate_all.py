import os

LangList = [
    "zh_CN",
    "zh_TW",
    "en_US",
    "es_ES",
    "fr_FR",
    "de_DE",
    "ja_JP",
    "ko_KR",
    "ru_RU",
    "pt_BR",
    "it_IT",
]

working = os.path.dirname(os.path.abspath(__file__))  # 工作目录
os.chdir(working)

for l in LangList:
    cmd = f'lupdate.exe "../../UmiOCR-data/qt_res/qml" -recursive -ts "{l}.ts"'
    os.system(cmd)
