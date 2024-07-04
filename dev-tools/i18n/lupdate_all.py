# 刷新所有翻译文本文件 .ts

import os
import sys
import xml.etree.ElementTree as ET

LangList = [
    "en_US",
    "zh_TW",
    "ja_JP",
    "fr_FR",
    "pt",
    # "nb_NO",
    # "it_IT",
    # "es_ES",
    # "de_DE",
    # "ko_KR",
    # "ru_RU",
    # "pt_BR",
]

working = os.path.dirname(os.path.abspath(__file__))  # 工作目录
os.chdir(working)

# 1. 扫描qml文件，生成 en_US.ts
for l in LangList:
    cmd = f'''lupdate.exe \
"../../UmiOCR-data/qt_res/qml" \
-recursive \
-no-obsolete \
-source-language "zh_CN" \
-target-language "{l}" \
-ts "release/{l}.ts"'''
    os.system(cmd)

sys.exit()  # Py翻译的部分 待定


# 2. 扫描py文件，生成 en_US_2.ts
def find_files(path, end=".py"):
    path = os.path.abspath(path)
    files_list = []
    for root, dirs, files in os.walk(path):
        # if "__pycache__"
        for file in files:
            if file.endswith(end):
                f = os.path.join(root, file)
                f = os.path.relpath(f, os.path.dirname(__file__))
                files_list.append(f)  # 使用相对路径，避免父路径的编码问题
    return files_list


input_files = find_files("../../UmiOCR-data/py_src")
input_str = "\\\n".join(input_files)
output_str = "release/" + "_2.ts\\\nrelease/".join(LangList) + "_2.ts"
temp_file = "temp.pro"  # 临时指令文件，用完删除
pro_str = f"""
CODECFORTR = UTF-8
CODECFORSRC = UTF-8
SOURCES = {input_str}
TRANSLATIONS = {output_str}
"""
with open(temp_file, "w", encoding="utf-8") as f:
    f.write(pro_str)

cmd = f"pyside2-lupdate.exe {temp_file}"
os.system(cmd)
print(output_str)
os.remove(temp_file)

# 3. 合并 en_US.ts 、 en_US_2.ts
for l in LangList:
    path_1 = f"release/{l}.ts"
    path_2 = f"release/{l}_2.ts"
    with open(path_2, "r", encoding="utf-8") as file:
        lines_2 = file.readlines()
    # py部分 无需翻译
    if len(lines_2) < 10:
        print(f"无需合并：{path_1}")
        continue
    # py部分 需合并
    # 解析xml
    tree_1 = ET.parse(path_1)
    root_1 = tree_1.getroot()
    root_2 = ET.parse(path_2).getroot()
    context_2 = root_2.findall("context")
    # 建立一个字典，存放所有 context
    context_dict = {c.find("name").text: c for c in root_1.findall("context")}
    # 遍历2，追加进字典
    # # 将2的context并入1
    for c2 in root_2.findall("context"):
        name = c2.find("name").text
        if name in context_dict:
            c1 = context_dict[name]
            for message_2 in c2.findall("message"):
                c1.append(message_2)
        else:
            root_1.append(c2)  # TODO: 正确性未验证
    # TODO: 保存时检查缩进格式
    tree_1.write(path_1, encoding="utf-8", xml_declaration=True)
    print(f"合并：{path_1}")
    os.remove(path_2)
