# 从data中提取、拼接文本
def getDataText(data):
    textOut = ""
    for i, tb in enumerate(data):
        textOut += tb["text"]
        textOut += tb["end"]
    return textOut
