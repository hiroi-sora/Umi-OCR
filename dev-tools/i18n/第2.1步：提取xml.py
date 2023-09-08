import xml.etree.ElementTree as ET

inFile = "翻译源文件.xml"
outFile = "翻译源.line.txt"

# 加载XML文件
tree = ET.parse(inFile)

# 获取根元素
root = tree.getroot()

# 遍历页面
data = []
for page in root:
    for message in page:
        if message.tag == "name":
            data.append([])
        else:
            location = message[0]
            filename = location.get("filename")
            source = message[1].text
            translation = message[2]
            if not source:
                source = message[2].text
                translation = message[3]
            data[-1].append({"source": source})
s = ""
for p in data:
    for d in p:
        s += d["source"].replace("\n", r"\n") + "\n"
with open(outFile, "w", encoding="utf-8") as f:
    f.write(s)

"""
请你充当翻译器，协助我完成一个软件的UI翻译工作。
我会输入多行文本，每行是一个原文。请你将其翻译为译文。
请保持原文的特殊格式，原文中的换行、%开头的标识符、mardown等格式予以保留。
首先，我们来做汉译英。
"""
