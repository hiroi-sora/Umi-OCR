import xml.etree.ElementTree as ET
import sys

inFile = sys.argv[1]
outFile = inFile + ".ts"
sourceFile = inFile[:-3] + "ts"

tree = ET.parse(sourceFile)
txt = open(inFile, encoding="utf-8").read()
txt = txt.split("\n")
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
            t = txt[tranIndex].replace(r"\n", "\n")  # \n转换行
            print("原文：", source.text)
            print("  译文：", t)
            tranIndex += 1
            translation.text = t
            if translation.attrib.get("type") is not None:
                translation.attrib.pop("type")
tree.write(outFile)
