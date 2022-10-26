# 通过 pipreqs 打包为 生成 requirements.txt

import os

dirPath = os.getcwd()

os.system(f'cd /d {dirPath}')
os.system(r'pipreqs ./ --encoding=utf8 --force --use-local')
