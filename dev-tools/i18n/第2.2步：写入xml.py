import xml.etree.ElementTree as ET

sourceFile = "翻译源文件.xml"
inFile = "zh_TW.line.txt"
outFile = "zh_TW.xml"
tree = ET.parse(sourceFile)
tran = open(inFile, encoding="utf-8").read()
tran = tran.split("\n")
tranIndex = 0

root = tree.getroot()

data = []
for page in root:
    for message in page:
        if message.tag == "name":
            pass
        else:
            location = message[0]
            filename = location.get("filename")
            source = message[1]
            translation = message[2]
            if not source.text:
                source = message[2]
                translation = message[3]
            t = tran[tranIndex]
            print("原文：", source.text)
            print("译文：", t)
            tranIndex += 1

            translation.attrib.pop("type")
            translation.text = t
tree.write(outFile)
