from utils.config import Config
from utils.logger import GetLog
from ocr.engine import MsnFlag
from ocr.msn import Msn

import tkinter as tk
import time

Log = GetLog()


class MsnBatch(Msn):

    def __init__(self, batList, setTableItem, textOutputInsert,
                 setRunning, clearTableItem, progressbar):
        self.progressbar = progressbar  # 进度条组件
        self.batList = batList
        self.setTableItem = setTableItem
        self.textOutputInsert = textOutputInsert
        self.setRunning = setRunning
        self.clearTableItem = clearTableItem
        self.isOutputFile = Config.get("isOutputFile")  # 是否输出文件
        self.isOutputDebug = Config.get("isOutputDebug")  # 是否输出调试
        self.isIgnoreNoText = Config.get("isIgnoreNoText")  # 是否忽略无字图片
        self.outputStyle = Config.get("outputStyle")  # 输出风格
        self.areaInfo = Config.get("ignoreArea")
        self.ocrToolPath = Config.get("ocrToolPath")  # 识别器路径
        self.configPath = Config.get("ocrConfig")[Config.get(  # 配置文件路径
            "ocrConfigName")]['path']
        self.argsStr = Config.get("argsStr")  # 启动参数
        if self.isOutputFile:
            outputPath = Config.get("outputFilePath")  # 输出路径（文件夹）
            suffix = ".txt" if self.outputStyle == 1 else ".md"
            self.outputFile = outputPath+"\\" + \
                Config.get("outputFileName")+suffix  # 输出文件

        Log.info(f'批量文本处理器初始化完毕！')

    def __output(self, outStr, type_):  # 输出字符串
        """
        debug ：调试信息
        text ：正文
        name ：文件名
        none ：不做修改
        """
        # 写入输出面板，无需格式
        self.textOutputInsert(f"\n{outStr}\n")

        # 写入本地文件，按照格式
        if self.isOutputFile:
            if self.outputStyle == 1:  # 纯文本风格
                if type_ == "debug":
                    outStr = f"```\n{outStr}```\n"
                elif type_ == "name":
                    outStr = f"\n\n≦ {outStr} ≧\n"
            elif self.outputStyle == 2:  # markdown风格
                if type_ == "debug":
                    outStr = f"```\n{outStr}```\n"
                elif type_ == "text":
                    outList = outStr.split("\n")
                    outStr = ""
                    for i in outList:
                        outStr += f"> {i}  \n"
                elif type_ == "name":
                    path = outStr.replace(" ", "%20")
                    outStr = f"---\n![{outStr}]({path})\n[{outStr}]({path})\n"
            with open(self.outputFile, "a", encoding='utf-8') as f:  # 追加写入本地文件
                f.write(outStr)

    def __analyzeText(self, oget, img):  # 分析一张图转出的文字
        def isInBox(aPos0, aPos1, bPos0, bPos1):  # 检测框左上、右下角，待测者左上、右下角
            return bPos0[0] >= aPos0[0] and bPos0[1] >= aPos0[1] and bPos1[0] <= aPos1[0] and bPos1[1] <= aPos1[1]

        def isIden():  # 是否识别区域模式
            if self.areaInfo["area"][1]:  # 需要检测
                for o in oget:  # 遍历每一个文字块
                    for a in self.areaInfo["area"][1]:  # 遍历每一个检测块
                        if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                            return True
        text = ""
        textDebug = ""  # 调试信息
        score = 0  # 平均置信度
        scoreNum = 0

        # 无需忽略区域
        if not self.areaInfo or not self.areaInfo["size"][0] == img["size"][0] or not self.areaInfo["size"][1] == img["size"][1]:

            for i in oget:
                text += i["text"]+"\n"
                score += i["score"]
                scoreNum += 1

        # 忽略模式2
        elif isIden():
            fn = 0  # 记录忽略的数量
            for o in oget:
                flag = True
                for a in self.areaInfo["area"][2]:  # 遍历每一个检测块
                    if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                        flag = False  # 踩到任何一个块，GG
                        break
                if flag:
                    text += o["text"]+"\n"
                    score += o["score"]
                    scoreNum += 1
                else:
                    fn += 1
            if self.isOutputDebug:
                textDebug = f"忽略模式2：忽略{fn}条\n"

        # 忽略模式1
        else:
            fn = 0  # 记录忽略的数量
            for o in oget:
                flag = True
                for a in self.areaInfo["area"][0]:  # 遍历每一个检测块
                    if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                        flag = False  # 踩到任何一个块，GG
                        break
                if flag:
                    text += o["text"]+"\n"
                    score += o["score"]
                    scoreNum += 1
                else:
                    fn += 1
            if self.isOutputDebug:
                textDebug = f"忽略模式1：忽略{fn}条\n"

        if text and not scoreNum == 0:  # 区域内有文本，计算置信度
            score /= scoreNum
            # score = str(score)  # 转文本
        else:
            score = 1  # 区域内没有文本，置信度为1
        return text, textDebug, score

    def onStart(self, num):
        Log.info('msnB: onStart')
        # 重置进度提示
        self.progressbar["maximum"] = num['all']
        self.progressbar["value"] = 0
        Config.set('tipsTop1', f'0s  0/{num["all"]}')
        Config.set('tipsTop2', f'0%')

        self.clearTableItem()  # 清空表格参数
        startStr = f"任务开始时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
        self.__output(startStr, "text")
        if self.isOutputDebug:
            startStr = f'已启用输出调试信息。\n识别器路径识别器路径：[{self.ocrToolPath}]\n配置文件路径：[{self.configPath}]\n启动参数：[{self.argsStr}]\n'
            if self.areaInfo:
                startStr += f'忽略区域：开启\n适用分辨率：{self.areaInfo["size"]}\n'
                startStr += f'忽略区域1：{self.areaInfo["area"][0]}\n'
                startStr += f'识别区域：{self.areaInfo["area"][1]}\n'
                startStr += f'忽略区域2：{self.areaInfo["area"][2]}\n'
            else:
                startStr += f"忽略区域：关闭\n"
            self.__output(startStr, "debug")
        self.setRunning(MsnFlag.running)

    def onGet(self, num, data):
        Log.info('msnB: onGet')
        self.progressbar["value"] = num['now']
        # 刷新进度提示
        Config.set('tipsTop2', f'{round((num["now"]/num["all"])*100)}%')
        Config.set(
            'tipsTop1', f'{round(num["time"], 2)}s  {num["now"]}/{num["all"]}')
        # 分析数据
        value = self.batList.get(index=num['index'])
        dataStr = ""
        textDebug = ""
        if data['code'] == 100:  # 成功
            dataStr, textDebug, score = self.__analyzeText(
                data['data'], value)  # 获取文字
            score = str(score)  # 转文本
        elif data['code'] == 101:  # 无文字
            score = "无文字"
        else:  # 识别失败
            dataStr = "识别失败"  # 不管开不开输出调试，都要输出报错
            dataStr += f"，错误码：{data['code']}\n错误信息：{str(data['data'])}\n"
            score = "失败"
        self.isNeedCopy = False  # 成功与否都将复制标志置F

        # 写入表格
        self.setTableItem(time=str(num['timeNow'])[:4],
                          score=score[:4], index=num['index'])
        # 格式化输出
        if self.isIgnoreNoText and not dataStr:
            return  # 忽略无字图片
        self.__output(value["name"], "name")
        if self.isOutputDebug:
            self.__output(
                f"识别耗时：{num['timeNow']}s 置信度：{score}\n{textDebug}", "debug")
        self.__output(dataStr, "text")

    def onStop(self):
        stopStr = f"\n任务结束时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
        self.__output(stopStr, "text")
        Log.info('msnB: onClose')
        self.setRunning(MsnFlag.none)
