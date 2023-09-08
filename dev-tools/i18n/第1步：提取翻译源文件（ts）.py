# 运行这个脚本，提取翻译文件。

# 资源文件使用方法：
# engine.load(f"res/qml/Main.qml")  # 原本
# engine.load(f"qrc:/qml/Main.qml")  # 现在


import os

# 填写代码目录
CODE_DIR = "../../UmiOCR-data/res/qml"

# 添加lupdate.exe所在路径
LUPDATE_EXE = "lupdate.exe"

# 填写要翻译的文件后缀
# SUFFIX = [".py", ".qml"]
SUFFIX = [".qml"]

# 填写要忽略的目录名称
IGNORE_DIR = [".runtime", ".site-packages", "__pycache__"]

# 填写生成ts的文件名
TS_NAME = "翻译源文件.ts"

# 自动生成文件列表
fileList = []


# 在dir目录下，搜索指定后缀的文件
def findFiles(dir):
    for filename in os.listdir(dir):  # 搜索当前路径
        filePath = os.path.join(dir, filename)
        # 判断是否为文件夹，如果是则递归调用自己
        if os.path.isdir(filePath):
            if os.path.basename(filePath) not in IGNORE_DIR:  # 排除忽略目录
                findFiles(filePath)
        # 如果是指定后缀名的文件，则打印相对路径
        else:
            suf = os.path.splitext(filePath)[-1]
            if suf in SUFFIX:
                fileList.append(filePath)


# 获取翻译指令
def getTsCmd(tsPath):
    tsCmd = f'{LUPDATE_EXE}'
    for s in fileList:
        tsCmd += f' "{s}"'
    tsCmd += f' -ts "{tsPath}"'
    return tsCmd


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 重新设定工作目录
    # 当前绝对路径
    nowDir = os.path.dirname(os.path.abspath(__file__))
    # 需翻译的目录
    codeDir = os.path.abspath(CODE_DIR)
    # 生成ts文件的路径
    tsPath = nowDir + "/" + TS_NAME
    print(f"""    ==========================
当前目录 {nowDir}
翻译目录 {codeDir}
提取器名称 {LUPDATE_EXE}
生成路径 {tsPath}
    ==========================""")

    findFiles(codeDir)
    print(f"搜索到{len(fileList)}个待翻译文件。")
    tsCmd = getTsCmd(tsPath)
    # print(f"{tsCmd}\n    ==========================")
    os.system(tsCmd)
    print(
        f"      生成为{TS_NAME}。\n      启动打包。没有报错就OKK\n    ==========================")


main()
