# Python 3.8.10
# (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)] on win32

from utils.config import Umi
from ui.win_main import MainWin

Umi.ver = '1.3.4-alpha.1'
Umi.pname = 'Umi-OCR.Rapid'
Umi.name = f'{Umi.pname} v{Umi.ver}'
Umi.website = 'https://github.com/hiroi-sora/Umi-OCR'
Umi.about = '测试版本。识别引擎采用RapidAI/RapidOcrOnnx。'


def main():
    MainWin()


if __name__ == "__main__":
    main()

# 打包使用 to_exe.py
