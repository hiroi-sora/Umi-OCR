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

for page in root:
    for message in page:
        if message.tag == "name":
            pass
        else:
            for item in message:
                if item.tag == "translation":
                    t = txt[tranIndex].replace(r"\n", "\n")  # \n转换行
                    item.text = t
                    # if item.attrib.get("type"):
                    #     item.attrib.pop("type")
                    tranIndex += 1
tree.write(outFile)
