# 从data中提取、拼接文本
def getDataText(data):
    textOut = ""
    l = len(data) - 1
    for i, tb in enumerate(data):
        textOut += tb["text"]
        if i < l:
            textOut += tb["end"]
    return textOut
