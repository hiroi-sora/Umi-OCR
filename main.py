# Python 3.8.10
# (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)] on win32

from config import Umi
from uiMain import MainWin

Umi.ver = '1.2.7 Alpha 5'
Umi.name = f'Umi-OCR v{Umi.ver}'
Umi.website = 'https://github.com/hiroi-sora/Umi-OCR'
Umi.about = '免费、开源的离线OCR软件'


def main():
    MainWin()


if __name__ == "__main__":
    main()

# cd /d D:\MyCode\PythonCode\Umi-OCR
# pyinstaller -F -w -i icon/icon.ico -n "Umi-OCR 批量图片转文字" main.py
