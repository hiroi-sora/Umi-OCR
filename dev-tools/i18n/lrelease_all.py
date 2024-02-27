# 将所有翻译文件转为二进制

import os

ts_files = []
for root, dirs, files in os.walk("release"):
    for file in files:
        if file.endswith(".ts"):
            ts_files.append(file)

print(ts_files)

for t in ts_files:
    cmd = f'''lrelease.exe \
"release/{t}"'''
    os.system(cmd)
