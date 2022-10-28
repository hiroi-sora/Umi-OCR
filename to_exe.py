# 通过 pyinstaller 打包为 exe

import os

dirPath = os.getcwd()

os.system(f'cd /d {dirPath}')
os.system(r'pyinstaller -F -w -i icon/icon.ico -n "Umi-OCR 文字识别" main.py')
