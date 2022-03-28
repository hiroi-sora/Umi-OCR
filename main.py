

from SelectAreaWin import SelectAreaWin

import os
import time
import asyncio  # 异步
import threading  # 线程
import subprocess  # 进程，管道
from PIL import Image
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from json import loads as jsonLoads
from windnd import hook_dropfiles  # 文件拖拽
from sys import platform as sysPlatform  # popen静默模式
from pyperclip import copy as pyperclipCopy  # 剪贴板


class Win:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Umi-OCR 批量图片转文字 v0.1")
        self.win.minsize(350, 520)
        self.win.geometry("360x520")
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)  # 窗口关闭
        self.imgDict = {}  # 当前载入的图片信息字典，key为表格组件id。必须为有序字典，python3.6以上默认是。
        self.areaInfo = None  # 特殊处理区域数据
        self.isRunning = 0  # 0未在运行，1正在运行，2正在停止

        def initTop():  # 顶部按钮
            tk.Frame(self.win, height=5).pack(side='top')
            vFrame1 = tk.Frame(self.win)
            vFrame1.pack(side='top', fill="x", padx=5)
            # 右侧按钮
            self.btnRun = tk.Button(
                vFrame1, text='开始任务', width=12, height=2,  command=self.run)
            self.btnRun.pack(side='right', padx=5)
            # 左侧文本和进度条
            vFrame2 = tk.Frame(vFrame1)
            vFrame2.pack(side='top', fill='x')
            labelUse = tk.Label(vFrame2, text="使用说明",
                                fg="gray", cursor="hand2")
            labelUse.pack(side='left', padx=5)
            labelUse.bind('<Button-1>', self.showInstructions)  # 绑定鼠标左键点击
            self.labelPercentage = tk.Label(vFrame2, text="0%")  # 进度百分比 99%
            self.labelPercentage.pack(side='right', padx=2)
            self.labelFractions = tk.Label(vFrame2, text="0/0")  # 进度分数 99/100
            self.labelFractions.pack(side='right')
            self.labelTime = tk.Label(vFrame2, text="0s")  # 已用时间 12.3s
            self.labelTime.pack(side='right', padx=5)
            self.progressbar = ttk.Progressbar(vFrame1)
            self.progressbar.pack(side='top', padx=5, fill="x")
        initTop()

        # 初始化选项卡组件
        self.notebook = ttk.Notebook(self.win)
        self.notebook.pack(expand=True, fill=tk.BOTH)  # 填满父组件

        def initTab1():  # 表格卡
            tabFrame = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebook.add(tabFrame, text=f'{"处理列表": ^10s}')
            vFrame1 = tk.Frame(tabFrame)
            vFrame1.pack(side='top', fill='x', pady=2)
            tk.Button(vFrame1, text=' 浏览 ',  command=self.openFileWin).pack(
                side='left', padx=5)
            tk.Label(vFrame1, text="或直接拖入").pack(side='left')
            tk.Button(vFrame1, text='清空表格', width=12, command=self.clearTable).pack(
                side='right')
            tk.Button(vFrame1, text='移除选中图片', width=12, command=self.delImgList).pack(
                side='right', padx=5)

            vFrame2 = tk.Frame(tabFrame)
            vFrame2.pack(side='top', fill='both')

            columns = ['name', 'time', 'score']
            self.table = ttk.Treeview(
                master=vFrame2,  # 父容器
                height=50,  # 表格显示的行数,height行
                columns=columns,  # 显示的列
                show='headings',  # 隐藏首列
            )
            # self.table.get
            hook_dropfiles(self.table, func=self.draggedImages)  # 注册文件拖入
            self.table.pack(expand=True, side="left", fill='both')
            self.table.heading('name', text='文件名称')
            self.table.heading('time', text='耗时')
            self.table.heading('score', text='置信度')
            self.table.column('name', minwidth=40)
            self.table.column('time', width=20, minwidth=20)
            self.table.column('score', width=30, minwidth=30)
            scroll = tk.Scrollbar(  # 绑定滚动条
                vFrame2, orient='vertical', command=self.table.yview)
            scroll.pack(side="left", fill='y')
            self.table["yscrollcommand"] = scroll.set
        initTab1()

        def initTab2():  # 输出卡
            self.tabFrameOutput = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebook.add(self.tabFrameOutput, text=f'{"识别内容": ^10s}')
            vFrame1 = tk.Frame(self.tabFrameOutput)
            vFrame1.pack(side='top', fill='x', pady=2)
            self.isAutoRoll = tk.IntVar()
            self.isAutoRoll.set(1)
            tk.Checkbutton(vFrame1, variable=self.isAutoRoll, text="自动滚动到底部").pack(
                side='left')
            tk.Button(vFrame1, text='清空版面', width=12,
                      command=lambda: self.textOutput.delete('1.0', tk.END)).pack(side='right')
            tk.Button(vFrame1, text='复制到剪贴板', width=12,
                      command=lambda: pyperclipCopy(self.textOutput.get("1.0", tk.END))).pack(side='right', padx=5)
            vFrame2 = tk.Frame(self.tabFrameOutput)
            vFrame2.pack(side='top', fill='both')
            scroll = tk.Scrollbar(  # 滚动条
                vFrame2, orient='vertical')
            scroll.pack(side="right", fill='y')
            self.textOutput = tk.Text(vFrame2, height=500, width=500)
            self.textOutput.pack(fill='both', side="left")
            scroll["command"] = self.textOutput.yview
            self.textOutput["yscrollcommand"] = scroll.set
        initTab2()

        def initTab3():  # 设置卡
            tabFrame = tk.Frame(self.notebook)  # 选项卡主容器
            self.notebook.add(tabFrame, text=f'{"设置": ^10s}')
            self.labelOptionTips = tk.Label(tabFrame, fg="red")  # 提示
            self.labelOptionTips.pack()
            # 输出文件设置
            vFrameOutFile = tk.LabelFrame(tabFrame, text="本地输出文件")
            vFrameOutFile.pack(side='top', fill='x', pady=2, padx=5)
            vFrameO1 = tk.Frame(vFrameOutFile)
            vFrameO1.pack(side='top', fill='x', pady=2)
            self.isOutputFile = tk.IntVar()
            self.isOutputFile.set(1)
            tk.Checkbutton(vFrameO1, variable=self.isOutputFile, text="启用 将识别内容写入txt文件").pack(
                side='left')
            tk.Label(vFrameOutFile, fg="gray", text="下面两项为空时，默认输出到第一张图片所在的文件夹").pack(
                side='top', padx=5)
            vFrameO2 = tk.Frame(vFrameOutFile)
            vFrameO2.pack(side='top', fill='x', pady=2)
            tk.Label(vFrameO2, text="输出目录：   ").pack(
                side='left', padx=5)
            self.enOutPath = tk.Entry(vFrameO2)
            self.enOutPath.pack(side='top', fill="x", padx=5)
            vFrameO3 = tk.Frame(vFrameOutFile)
            vFrameO3.pack(side='top', fill='x', pady=2)
            tk.Label(vFrameO3, text="输出文件名：").pack(side='left', padx=5)
            self.enOutName = tk.Entry(vFrameO3)
            self.enOutName.pack(side='top', fill="x", padx=5)
            # 忽略区域
            vFrameArea = tk.LabelFrame(tabFrame, text="忽略图片中某些区域内的文字")
            vFrameArea.pack(side='top', fill='x', pady=2, padx=5)
            vFrameA1 = tk.Frame(vFrameArea)
            vFrameA1.pack(side='top', fill='x', pady=2)
            tk.Button(vFrameA1, text='添加忽略区域',
                      command=self.openSelectArea).pack(side="left", padx=5)
            tk.Button(vFrameA1, text='清空所有区域',
                      command=self.clearArea).pack(side="left")
            self.areaLabel = tk.Label(vFrameA1, text="待添加", padx=5)
            self.areaLabel.pack(side="right")
            self.canvasHeight = 140  # 画板高度不变，宽度根据选区回传数据调整
            self.canvas = tk.Canvas(vFrameArea, width=249, height=self.canvasHeight,
                                    bg="black")
            self.canvas.pack(side='top')
            # 识别器exe与图片后缀设置
            vFrameEXE = tk.LabelFrame(tabFrame, text="识别器设置  [切换多国语言和不同格式图片]")
            vFrameEXE.pack(side='top', fill='x', pady=2, padx=5)
            vFrame5 = tk.Frame(vFrameEXE)
            vFrame5.pack(side='top', fill='x', pady=2)
            tk.Label(vFrame5, text="识别器路径：").pack(
                side='left', padx=5)
            self.enEXE = tk.Entry(vFrame5)
            self.enEXE.pack(side='top', fill="x", padx=5)
            self.enEXE.insert(0, "PaddleOCR_Green\\PaddleOCR_json.exe")
            vFrame4 = tk.Frame(vFrameEXE)
            vFrame4.pack(side='top', fill='x', pady=2)
            tk.Label(vFrame4, text="图片后缀：   ").pack(
                side='left', padx=5)
            self.enInSuffix = tk.Entry(vFrame4)
            self.enInSuffix.pack(side='top', fill="x", padx=5)
            self.enInSuffix.insert(
                0, ".jpg .jpeg .JPG .JPEG .png .PNG .webp .WEBP")
        initTab3()

        self.win.mainloop()

    def openSelectArea(self):  # 打开选择区域
        if not self.isRunning == 0:
            return
        defaultPath = ""
        if self.imgDict:
            defaultPath = next(iter(self.imgDict.values()))["path"]
        self.win.attributes("-disabled", 1)  # 禁用父窗口
        SelectAreaWin(self.closeSelectArea, defaultPath)

    def closeSelectArea(self, info=None):  # 关闭选择区域，获取选择区域数据
        self.win.attributes("-disabled", 0)  # 启用父窗口
        if not info:
            return
        self.areaInfo = info
        self.areaLabel["text"] = f"生效分辨率：{info[0][0]}x{info[0][1]}"
        self.canvas.delete(tk.ALL)  # 清除画布
        scale = self.canvasHeight / info[0][1]  # 显示缩放比例
        width = int(self.canvasHeight * (info[0][0] / info[0][1]))
        self.canvas["width"] = width
        areaColor = ["red", "green", "gold1"]
        for i in range(3):
            for a in info[1][i]:
                x0, y0 = a[0][0]*scale, a[0][1]*scale,
                x1, y1 = a[1][0]*scale, a[1][1]*scale,
                self.canvas.create_rectangle(
                    x0, y0, x1, y1,  fill=areaColor[i])  # 绘制新图

    def draggedImages(self, paths):  # 拖入图片
        if not self.isRunning == 0:
            return
        pathList = []
        for p in paths:  # byte转字符串
            pathList.append(p.decode("gbk"))
        self.addImagesList(pathList)

    def openFileWin(self):  # 打开选择文件窗
        if not self.isRunning == 0:
            return
        suf = self.enInSuffix.get()  # 许可后缀
        paths = tk.filedialog.askopenfilenames(
            title='选择图片', filetypes=[('图片', suf)])
        self.addImagesList(paths)

    def addImagesList(self, paths):
        suf = self.enInSuffix.get().split()  # 许可后缀
        for path in paths:  # 遍历拖入的所有路径
            if os.path.isdir(path):  # 若是目录
                subFiles = os.listdir(path)  # 遍历子文件
                for s in subFiles:
                    self.addImage(path+"\\"+s, suf)  # 添加
            elif os.path.isfile(path):  # 若是文件：
                self.addImage(path, suf)  # 直接添加

    def addImage(self, path, okSuf=None):  # 添加一张图片。传入路径，许可后缀。
        path = path.replace("/", "\\")  # 浏览是左斜杠，拖入是右斜杠；需要统一
        if okSuf and os.path.splitext(path)[1] not in okSuf:
            return  # 需要判别许可后缀 且 文件后缀不在许可内，不添加。
        # 检测是否重复
        for key, value in self.imgDict.items():
            if value["path"] == path:
                return
        p = os.path.abspath(os.path.join(path, os.pardir))  # 父文件夹
        if not self.enOutPath.get():  # 初始化输出路径
            self.enOutPath.delete('0', tk.END)
            self.enOutPath.insert(0, p)
        if not self.enOutName.get():  # 初始化输出文件名
            n = f"[转文字]_{os.path.basename(p)}.txt"
            self.enOutName.delete('0', tk.END)
            self.enOutName.insert(0, n)
        name = os.path.basename(path)  # 带后缀的文件名
        tableInfo = (name, "", "")
        id = self.table.insert('', 'end', values=tableInfo)  # 添加到表格组件中
        info = {"name": name, "path": path, "size": Image.open(path).size}
        self.imgDict[id] = (info)  # 添加到列表中

    def clearTable(self):  # 清空表格
        if not self.isRunning == 0:
            return
        self.progressbar["value"] = 0
        self.labelPercentage["text"] = "0%"
        self.labelFractions["text"] = "0/0"
        self.labelTime["text"] = "0s"
        self.enOutPath.delete('0', tk.END)
        self.enOutName.delete('0', tk.END)
        self.imgDict = {}
        chi = self.table.get_children()
        for i in chi:
            self.table.delete(i)  # 表格组件移除

    def clearArea(self):  # 清空忽略区域
        self.areaInfo = None
        self.areaLabel["text"] = "待添加"
        self.canvas.delete(tk.ALL)  # 清除画布
        self.canvas["width"] = int(self.canvasHeight * (16/9))

    def delImgList(self):  # 图片列表中删除选中
        if not self.isRunning == 0:
            return
        chi = self.table.selection()
        for i in chi:
            self.table.delete(i)
            del self.imgDict[i]  # 字典删除

    def setRunning(self, r):  # 设置运行状态。0停止，1运行中，2停止中
        self.isRunning = r
        if r == 0:
            self.btnRun["text"] = "开始任务"
            self.btnRun['state'] = "normal"
            self.labelOptionTips["text"] = ""
        elif r == 1:
            self.btnRun["text"] = "停止任务"
            self.btnRun['state'] = "normal"
            self.labelOptionTips["text"] = " 任务进行中。不要改动任何配置！！ "
        elif r == 2:
            self.btnRun["text"] = "正在停止"
            self.btnRun['state'] = "disable"

    def run(self):  # 开始任务，创建新线程和事件循环
        if self.isRunning == 0:  # 未在运行，开始运行
            if not self.imgDict:
                return
            # 检测识别器存在
            exePath = self.enEXE.get()
            if not os.path.exists(exePath):
                tk.messagebox.showerror(
                    '警告', f'未在以下地址找到识别器！\n{exePath}')
                return
            # 创建输出文件
            if self.isOutputFile.get() == 1:
                outPath = self.enOutPath.get() + "\\" + self.enOutName.get()
                try:
                    if os.path.exists(outPath):  # 文件存在
                        os.remove(outPath)  # 删除文件
                    open(outPath, 'w').close()  # 创建文件
                except FileNotFoundError:
                    tk.messagebox.showerror(
                        '创建文件失败', f'创建输出文件失败。请检查以下地址是否正确。\n{outPath}')
                    return
                except Exception as e:
                    tk.messagebox.showerror(
                        '创建文件失败', f'创建输出文件失败。文件地址：\n{outPath}\n\n错误信息：\n{e}')
                    return
            self.setRunning(1)
            # 在当前线程下创建时间循环，在start_loop里面启动它
            newLoop = asyncio.new_event_loop()
            # 通过当前线程开启新的线程去启动事件循环
            threading.Thread(target=self.getLoop, args=(newLoop,)).start()
            # 在新线程中事件循环不断“游走”执行
            asyncio.run_coroutine_threadsafe(self.run_(), newLoop)
        elif self.isRunning == 1:  # 正在运行，停止运行
            self.setRunning(2)

    def getLoop(self, loop):  # 获取事件循环
        self.loop = loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def run_(self):  # 异步，执行任务
        isOutputFile = self.isOutputFile.get()
        areaInfo = self.areaInfo
        if isOutputFile == 1:
            outPath = self.enOutPath.get() + "\\" + self.enOutName.get()  # 输出文件

        def output(str_):  # 输出字符串
            if isOutputFile == 1:
                with open(outPath, "a", encoding='utf-8') as f:  # 追加写入本地文件
                    f.write(str_)
            self.textOutput.insert(tk.END, str_)  # 1写入输出面板
            if self.isAutoRoll.get():  # 需要自动滚动
                self.textOutput.see(tk.END)

        def close():  # 关闭所有异步相关的东西
            del self.ocr  # 关闭OCR进程
            self.loop.stop()  # 关闭异步事件循环
            self.setRunning(0)
            self.labelPercentage["text"] = "已终止"
            # print("异步任务结束！")

        def getText(oget, img):  # 分析一张图转出的文字
            def isInBox(aPos0, aPos1, bPos0, bPos1):  # 检测框左上、右下角，待测者左上、右下角
                return bPos0[0] > aPos0[0] and bPos0[1] > aPos0[1] and bPos1[0] < aPos1[0] and bPos1[1] < aPos1[1]

            def isIden():  # 是识别区域模式
                if areaInfo[1][1]:  # 需要检测
                    for o in oget:  # 遍历每一个文字块
                        for a in areaInfo[1][1]:  # 遍历每一个检测块
                            if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                                return True
            text = ""
            textLog = ""
            score = 0  # 平均置信度
            scoreNum = 0
            if not areaInfo or not areaInfo[0][0] == img["size"][0] or not areaInfo[0][1] == img["size"][1]:
                for i in oget:
                    text += i["text"]+"\n"
                    score += i["score"]
                    scoreNum += 1
            # 判断，是忽略模式2
            elif isIden():
                fn = 0  # 记录忽略的数量
                for o in oget:
                    flag = True
                    for a in areaInfo[1][2]:  # 遍历每一个检测块
                        if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                            flag = False  # 踩到任何一个块，GG
                            break
                    if flag:
                        text += o["text"]+"\n"
                        score += o["score"]
                        scoreNum += 1
                    else:
                        fn += 1
                # textLog = f"〔忽略模式2：忽略{fn}条〕\n"
            else:  # 否则，忽略模式1
                fn = 0  # 记录忽略的数量
                for o in oget:
                    flag = True
                    for a in areaInfo[1][0]:  # 遍历每一个检测块
                        if isInBox(a[0], a[1], (o["box"][0], o["box"][1]), (o["box"][4], o["box"][5])):
                            flag = False  # 踩到任何一个块，GG
                            break
                    if flag:
                        text += o["text"]+"\n"
                        score += o["score"]
                        scoreNum += 1
                    else:
                        fn += 1
                # textLog = f"〔忽略模式1：忽略{fn}条〕\n"
            if text and not scoreNum == 0:
                text = textLog+text
                score /= scoreNum
                score = str(score)
            else:
                text = textLog+"所有文字在忽略范围内\n"
                score = "全部忽略"
            return text, score

        # 开始
        startStr = f"\n任务开始时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
        if areaInfo:
            startStr += f"忽略区域：开启\n适用分辨率：{areaInfo[0]}\n"
            startStr += f"忽略区域1：{areaInfo[1][0]}\n"
            startStr += f"识别区域：{areaInfo[1][1]}\n"
            startStr += f"忽略区域2：{areaInfo[1][2]}\n"
        else:
            startStr += f"忽略区域：关闭\n"
        output(startStr)
        # 创建OCR进程
        exe = self.enEXE.get()
        cwd = os.path.abspath(os.path.join(exe, os.pardir))  # exe父文件夹
        self.ocr = CallingOCR(exe, cwd)
        # 计数器
        allNum, nowNum = len(self.imgDict), 0
        startTime = time.time()  # 开始时间
        costTime = 0
        self.progressbar["maximum"] = allNum
        self.progressbar["value"] = 0
        self.labelPercentage["text"] = "0%"
        self.labelFractions["text"] = f"0/{allNum}"
        self.labelTime["text"] = "0s"
        numOK = 0  # 成功数量
        numNON = 0  # 不存在数量
        numERR = 0  # 出错数量
        # 清空表格参数
        for key in self.imgDict.keys():
            self.table.set(key, column='time', value="")
            self.table.set(key, column='score', value="")

        # 主任务循环
        for key, value in self.imgDict.items():
            try:
                if not self.isRunning == 1:  # 需要停止
                    close()
                    return
                oget = self.ocr.run(value["path"])  # 调用图片识别
                # 计数
                nowNum += 1  # 当前完成个数
                costTimeNow = time.time() - startTime  # 当前总花费时间
                needTimeStr = str(costTimeNow-costTime)  # 单个花费时间
                costTime = round(costTimeNow, 2)  # 刷新花费时间
                self.progressbar["value"] = nowNum
                self.labelPercentage["text"] = f"{round((nowNum/allNum)*100)}%"
                self.labelFractions["text"] = f"{nowNum}/{allNum}"
                self.labelTime["text"] = f"{costTime}s"
                self.table.set(key, column='time',
                               value=needTimeStr[:4])  # 时间写入表格
                # 分析数据
                if isinstance(oget, dict):  # 识别失败
                    numERR += 1
                    dataStr = "识别失败"
                    if "text" in oget.keys():  # 在python中报的错
                        dataStr += f"，python报错\n原因：{oget['error']}\nC++模块返回值：{oget['text']}\n"
                    elif "error" in oget.keys():  # 在c++中报的错
                        dataStr += f"，C++报错\n原因：{oget['error']}\n"
                    score = "失败"
                elif len(oget) == 0:
                    numNON += 1
                    dataStr = "未识别到文字\n"
                    score = "无文字"
                else:
                    numOK += 1
                    dataStr, score = getText(oget, value)  # 获取文字
                writeStr = f'\n\n≦ {value["name"]} ≧\n〔识别耗时：{needTimeStr}s 置信度：{score}〕\n{dataStr}'
                self.table.set(key, column='score', value=score[:4])  # 写入表格
                output(writeStr)
            except Exception as e:
                tk.messagebox.showerror(
                    '图片识别异常', f'图片识别异常：\n{value["name"]}\n异常信息：\n{e}')
                # print(f'出问题了：{value["name"]}\n{e}')
        # 结束
        endTime = time.time()
        endStr = f"\n\n\n任务结束时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endTime))}\n"
        endStr += f"任务耗时（秒）：        {endTime-startTime}\n"
        endStr += f"单张平均耗时：          {(endTime-startTime)/allNum}\n"
        endStr += f"识别正常 的图片数量：    {numOK}\n"
        endStr += f"未识别到文字 的图片数量：{numNON}\n"
        endStr += f"识别失败 的图片数量：    {numERR}\n\n"
        output(endStr)
        close()  # 完成后关闭
        self.labelPercentage["text"] = "完成！"

    def showInstructions(self, e):  # 打开使用说明
        if not self.isRunning == 0:
            tk.messagebox.showwarning(
                '任务进行中', '停止任务后，再打开软件说明')
            return
        self.notebook.select(self.tabFrameOutput)  # 切换到输出选项卡
        outputNow = self.textOutput.get("1.0", tk.END)
        if outputNow and not outputNow == "\n":  # 输出面板内容存在，且不是单换行（初始状态）
            if not tkinter.messagebox.askokcancel('提示', '将清空输出面板。要继续吗？'):
                return
            self.textOutput.delete('1.0', tk.END)
        self.textOutput.insert(tk.END, UmiOCR)

    def onClose(self):  # 关闭窗口事件
        if self.isRunning == 0:  # 未在运行
            self.win.destroy()  # 直接关闭
        if not self.isRunning == 0:  # 正在运行，需要停止
            self.setRunning(2)
            # self.win.after( # 非阻塞弹出提示框
            #     0, lambda: tk.messagebox.showinfo('请稍候', '等待进程终止，程序稍后将关闭'))
            self.win.after(100, self.waitClose)  # 等待关闭

    def waitClose(self):  # 等待进程关闭后销毁窗口
        if self.isRunning == 0:
            self.win.destroy()  # 销毁窗口
        else:
            self.win.after(100, self.waitClose)  # 等待关闭


class CallingOCR:
    def __init__(self, exePath, cwd=None):
        """初始化识别器。\n
        传入识别器exe路径，子进程目录(exe父目录)"""
        startupinfo = None  # 静默模式设置
        if 'win32' in str(sysPlatform).lower():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        self.ret = subprocess.Popen(  # 打开管道
            exePath,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            startupinfo=startupinfo  # 开启静默模式
        )
        self.ret.stdout.readline()  # 读掉第一行

    def run(self, imgPath):
        """对一张图片文字识别。
        输入图片路径。\n
        识别成功时，返回列表，每项是一组文字的信息。\n
        识别失败时，返回字典 {error:异常信息，text:(若存在)原始识别字符串} 。"""
        if not imgPath[-1] == "\n":
            imgPath += "\n"
        try:
            self.ret.stdin.write(imgPath.encode("gbk"))
            self.ret.stdin.flush()
        except Exception as e:
            return {"error": f"向识别器进程写入图片地址失败，疑似该进程已崩溃。{e}", "text": ""}
        try:
            getStr = self.ret.stdout.readline().decode('utf-8', errors='ignore')
        except Exception as e:
            if imgPath[-1] == "\n":
                imgPath = imgPath[:-1]
            return {"error": f"读取识别器进程输出值失败，疑似传入了不存在或无法识别的图片【{imgPath}】。{e}", "text": ""}
        try:
            return jsonLoads(getStr)
        except Exception as e:
            if imgPath[-1] == "\n":
                imgPath = imgPath[:-1]
            return {"error": f"识别器输出值反序列化JSON失败，疑似传入了不存在或无法识别的图片【{imgPath}】。{e}", "text": getStr}

    def __del__(self):
        self.ret.kill()  # 关闭子进程


UmiOCR = """

UmiOCR 批量图片转文字工具 v0.1


本软件
"""

if __name__ == "__main__":
    Win()

# pyinstaller - F main.py - w
