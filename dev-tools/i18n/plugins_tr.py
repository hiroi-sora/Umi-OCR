import re
import csv
import sys

inFile = sys.argv[1]
outFile = "待翻译.csv"


def extract_strings_from_file(file_path):
    pattern = r'tr\(["\']([^"\']*)["\']\)'  # 正则表达式模式
    strings = []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        matches = re.findall(pattern, content)  # 使用正则表达式查找匹配项

        for match in matches:
            strings.append(match)

    return strings


tr_strs = extract_strings_from_file(inFile)
lines = [["key", "en_US"]]
for i in tr_strs:
    lines.append([i, ""])

with open(outFile, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    for i in lines:
        writer.writerow(i)

print("插件翻译完成：\n", inFile)
