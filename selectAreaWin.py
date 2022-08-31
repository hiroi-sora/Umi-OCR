from callingOCR import CallingOCR  # OCR调用接口
from asset import IconPngBase64  # 资源
from config import Config

import os
import tkinter as tk
import tkinter.messagebox
from windnd import hook_dropfiles  # 文件拖拽
from PIL import Image, ImageTk


class SelectAreaWin:
    def __init__(self, closeSendData=None, defaultPath="", exePath="PaddleOCR-json\PaddleOCR_json.exe"):
        self.closeSendData = closeSendData  # 向父窗口发送数据的接口
        self.cW = 960  # 画板尺寸
        self.cH = 540
        self.areaColor = ["red", "green",  # 各个矩形区域的标志颜色
                          "darkorange", "white"]

        # def initWin():  # 初始化主窗口
        # 主窗口
        self.win = tk.Toplevel()
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)
        self.win.title("选择区域")
        self.win.resizable(False, False)  # 禁止窗口拉伸
        # 变量初始化
        self.imgSize = (-1, -1)  # 图像尺寸，初次加载时生效。
        self.imgScale = -1  # 图片缩放比例
        self.imgSizeText = tk.StringVar(value="未设定")
        self.area = [[], [], []]  # 存储各个矩形区域的列表
        self.areaHistory = []  # 绘图历史，撤销用
        self.areaTextRec = []  # 文字区域提示框
        self.areaType = -1  # 当前绘图模式
        self.areaTypeIndex = [-1, -1, -1]  # 当前绘制的矩形的序号
        # 图标
        self.iconImg = tkinter.PhotoImage(
            data=IconPngBase64)  # 载入图标，base64转
        self.win.iconphoto(False, self.iconImg)  # 设置窗口图标
        # initWin()

        # def initPanel():  # 初始化面板
        tk.Frame(self.win, height=10).pack(side='top')
        ctrlFrame = tk.Frame(self.win)
        ctrlFrame.pack(side='top', fill='y')
        ctrlF0 = tk.Frame(ctrlFrame)
        ctrlF0.pack(side='left')
        tk.Label(ctrlF0, text="【图像分辨率】").pack()
        tk.Label(ctrlF0, textvariable=self.imgSizeText).pack()
        tk.Label(ctrlF0, text="不符合该分辨率的图片\n忽略区域设置不会生效",
                 fg='gray', wraplength=120).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF1 = tk.Frame(ctrlFrame)
        ctrlF1.pack(side='left')
        self.buttons = [None, None, None]
        self.buttons[0] = tk.Button(ctrlF1, text='+忽略区域 A', width=23, height=2, fg=self.areaColor[0], bg=self.areaColor[3],
                                    command=lambda: self.changeMode(0))
        self.buttons[0].pack()
        tk.Label(ctrlF1, text="处于[忽略区域 A]内\n的矩形虚线文字块将被忽略。",
                 wraplength=180).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF2 = tk.Frame(ctrlFrame)
        ctrlF2.pack(side='left')
        self.buttons[1] = tk.Button(ctrlF2, text='+识别区域', width=23, height=2, fg=self.areaColor[1], bg=self.areaColor[3],
                                    command=lambda: self.changeMode(1))
        self.buttons[1].pack()
        tk.Label(ctrlF2, text="若[识别区域]内存在虚线块，\n则[忽略区域 A]失效。",
                 wraplength=180).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF3 = tk.Frame(ctrlFrame)
        ctrlF3.pack(side='left')
        self.buttons[2] = tk.Button(ctrlF3, text='+忽略区域 B', width=23, height=2, fg=self.areaColor[2], bg=self.areaColor[3],
                                    command=lambda: self.changeMode(2))
        self.buttons[2].pack()
        tk.Label(ctrlF3, text="当[忽略区域 A]失效时，\n[忽略区域 B]生效。",
                 wraplength=180).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF4 = tk.Frame(ctrlFrame)
        ctrlF4.pack(side='left')
        tk.Button(ctrlF4, text='清空', width=10,
                  command=self.clearCanvas).pack()
        tk.Button(ctrlF4, text='撤销\nCtrl+Shift+Z', width=10,
                  command=self.revokeCanvas).pack(pady=5)
        self.win.bind("<Control-Z>", self.revokeCanvas)  # 绑定撤销组合键，带shift
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        tk.Button(ctrlFrame, text='完成', width=8,
                  command=lambda: self.onClose(False)).pack(side="left", fill="y")
        tipsFrame = tk.Frame(self.win)
        tipsFrame.pack(fill="x")
        self.isAutoOCR = tk.IntVar()
        self.isAutoOCR.set(1)
        tk.Checkbutton(tipsFrame, variable=self.isAutoOCR, text="启用 图片分析").pack(
            side='left', padx=30)
        tk.Label(tipsFrame, text="   ↓ ↓ ↓ 将任意图片拖入下方预览。然后点击按钮切换画笔，在图片上按住左键框选出想要的区域。",
                 fg='gray').pack(side='left')
        tk.Label(tipsFrame, text="同一种区域可绘制多个方框。", fg='blue').pack(side='left')
        tk.Label(tipsFrame, text="↓ ↓ ↓", fg='gray').pack(side='left')
        # initPanel()

        # def initCanvas():  # 初始化绘图板
        self.canvas = tk.Canvas(self.win, width=self.cW, height=self.cH,
                                bg="gray", cursor="plus", borderwidth=0)
        self.canvas.bind("<Button-1>", self.mouseDown)  # 鼠标点击
        self.canvas.bind("<B1-Motion>", self.mouseMove)  # 鼠标移动
        self.canvas.pack()
        hook_dropfiles(self.win, func=self.draggedFiles)  # 注册文件拖入
        self.canvasImg = None  # 当前在显示的图片
        # initCanvas()

        # def initOCR():  # 初始化识别器
        self.ocr = None
        if not os.path.exists(exePath):
            tk.messagebox.showerror(
                '遇到了一点小问题', f'未在以下路径找到识别器：\n[{exePath}]')
            return
        # 创建OCR进程
        configPath = Config.get("ocrConfig")[Config.get(  # 配置文件路径
            "ocrConfigName")]['path']
        argsStr = Config.get("argsStr")  # 启动参数
        try:
            self.ocr = CallingOCR(exePath, configPath, argsStr)
        except Exception as e:
            tk.messagebox.showerror(
                '遇到了亿点小问题',
                f'识别器初始化失败：[{e}]\n\n识别器路径：[{exePath}]\n\n配置文件路径：[{configPath}]\n\n启动参数：[{argsStr}]\n\n请检查以上配置有无问题！')
            return
        # initOCR()

        if defaultPath:  # 打开默认图片
            self.loadImage(defaultPath)

        self.win.mainloop()

    def onClose(self, isAsk=True):  # 点击关闭。isAsk为T时询问。

        def getData():  # 将数据传给接口，然后关闭窗口
            area = [[], [], []]
            for i in range(3):
                for a in self.area[i]:
                    a00, a01, a10, a11 = round(
                        a[0][0]/self.imgScale), round(a[0][1]/self.imgScale), round(a[1][0]/self.imgScale), round(a[1][1]/self.imgScale)
                    if a00 > a10:  # x对调
                        a00, a10 = a10, a00
                    if a01 > a11:  # y对调
                        a01, a11 = a11, a01
                    area[i].append([(a00, a01), (a10, a11)])
            return {"size": self.imgSize, "area": area}

        if self.area[0] or self.area[1] or self.area[2]:  # 数据存在
            if isAsk:  # 需要问
                if tk.messagebox.askokcancel('关闭窗口', '要应用选区吗？'):  # 需要应用
                    Config.set("ignoreArea", getData())
            else:  # 不需要问
                Config.set("ignoreArea", getData())
        if self.closeSendData:  # 通信接口存在，则回传数据
            self.closeSendData()
        if self.ocr:
            del self.ocr  # 关闭OCR进程
        self.win.destroy()  # 销毁窗口

    def draggedFiles(self, paths):  # 拖入文件
        self.loadImage(paths[0].decode("gbk"))

    def loadImage(self, path):  # 载入新图片
        """载入图片"""
        try:
            img = Image.open(path)
        except Exception as e:
            tk.messagebox.showwarning(
                "遇到了一点小问题", f"图片载入失败。图片地址：\n{path}\n\n错误信息：\n{e}")
            return
        # 检测图片大小
        if self.imgSize == (-1, -1):  # 初次设定
            self.imgSize = img.size
            # 计算 按宽和高 分别缩放的比例
            sw, sh = self.cW/img.size[0], self.cH/img.size[1]
            if sw > sh:  # 测试，按宽、还是高缩放，刚好填满画布
                self.imgReSize = (round(img.size[0]*sh), self.cH)
            else:
                self.imgReSize = (self.cW, round(img.size[1]*sw))
            # 记录缩放系数，原分辨率*系数=绘制分辨率
            self.imgScale = self.imgReSize[0]/self.imgSize[0]
            self.imgSizeText.set(f'{self.imgSize[0]}x{self.imgSize[1]}')
        elif not self.imgSize == img.size:  # 尺寸不符合
            tk.messagebox.showwarning("图片尺寸错误！",
                                      f"当前图像尺寸限制为{self.imgSize[0]}x{self.imgSize[1]}，不允许加载{img.size[0]}x{img.size[1]}的图片。\n若要解除限制、更改为其他分辨率，请点击“清空”后重新拖入图片。")
            return
        self.clearCanvasImage()  # 清理上次绘制的图像

        # OCR识别
        def runOCR():
            if self.ocr and self.isAutoOCR.get():
                # 任务前：显示提示信息
                self.win.title(f"分析中…………")  # 改变标题
                pathStr = path if len(
                    path) <= 50 else path[:50]+"……"  # 路径太长显示不全，截取
                canvasText = self.canvas.create_text(self.cW/2, self.cH/2, font=('', 15, 'bold'), fill='white', anchor="c",
                                                     text=f'图片分析中，请稍候……\n\n\n\n{pathStr}')
                self.win.update()  # 刷新窗口
                # 开始识别，耗时长
                oget = self.ocr.run(path)
                # 任务后：刷新提示信息
                self.canvas.delete(canvasText)  # 删除提示文字
                if oget["code"] == 100:  # 存在内容
                    for o in oget["data"]:  # 绘制矩形框
                        p1x = round(o['box'][0]*self.imgScale)
                        p1y = round(o['box'][1]*self.imgScale)
                        p2x = round(o['box'][4]*self.imgScale)
                        p2y = round(o['box'][5]*self.imgScale)
                        r1 = self.canvas.create_rectangle(
                            p1x, p1y, p2x, p2y, outline='white', width=1)  # 绘制白实线基底
                        r2 = self.canvas.create_rectangle(
                            p1x, p1y, p2x, p2y, outline='black', width=1, dash=4)  # 绘制黑虚线表层
                        self.canvas.tag_lower(r2)  # 移动到最下方
                        self.canvas.tag_lower(r1)
                        self.areaTextRec.append(r1)
                        self.areaTextRec.append(r2)
                elif not oget["code"] == 101:  # 发生异常
                    tk.messagebox.showwarning(
                        "遇到了一点小问题", f"图片分析失败。图片地址：\n{path}\n\n错误信息：\n{str(oget['data'])}")
        runOCR()
        self.win.title(f"选择区域 {path}")  # 改变标题
        # 缓存图片并显示
        img = img.resize(self.imgReSize, Image.ANTIALIAS)  # 改变图片大小
        self.imgFile = ImageTk.PhotoImage(img)  # 缓存图片
        self.canvasImg = self.canvas.create_image(
            0, 0, anchor='nw', image=self.imgFile)  # 绘制图片
        self.canvas.tag_lower(self.canvasImg)  # 该元素移动到最下方，防止挡住矩形们

    def changeMode(self, type_):  # 切换绘图模式
        if self.imgSize == (-1, -1):
            return
        self.areaType = type_
        for b in self.buttons:
            b["state"] = tk.NORMAL  # 启用所有按钮
            b["bg"] = self.areaColor[3]
        self.buttons[type_]["state"] = tk.DISABLED  # 禁用刚按下的按钮
        self.buttons[type_]["bg"] = self.areaColor[type_]  # 切换背景颜色

    def clearCanvasImage(self):  # 清除画布上的图片其文字框，不清理忽略框
        if self.canvasImg:  # 删除图片
            self.canvas.delete(self.canvasImg)
        for t in self.areaTextRec:  # 删除文字框
            self.canvas.delete(t)
        self.areaTextRec = []

    def clearCanvas(self):  # 清除画布
        self.win.title(f"选择区域")  # 改变标题
        self.area = [[], [], []]
        self.areaHistory = []
        self.areaTextRec = []
        self.areaType = -1
        self.areaTypeIndex = [-1, -1, -1]
        self.imgSize = (-1, -1)
        self.imgSizeText.set("未设定")
        self.canvas.delete(tk.ALL)
        for b in self.buttons:
            b["state"] = tk.NORMAL  # 启用所有按钮
            b["bg"] = self.areaColor[3]

    def revokeCanvas(self, e=None):  # 撤销一步
        if len(self.areaHistory) == 0:
            return
        self.canvas.delete(self.areaHistory[-1]["id"])  # 删除历史记录中最后绘制的矩形
        self.area[self.areaHistory[-1]["type"]].pop()  # 删除对应类型的最后一个矩形数据
        self.areaHistory.pop()  # 删除历史记录

    def mouseDown(self, event):  # 鼠标按下，生成新矩形
        if self.areaType == -1:
            return
        x, y = event.x, event.y
        if x > self.imgReSize[0]:  # 防止越界
            x = self.imgReSize[0]
        elif x < 0:
            x = 0
        if y > self.imgReSize[1]:
            y = self.imgReSize[1]
        elif y < 0:
            y = 0
        c = self.areaColor[self.areaType]
        id = self.canvas.create_rectangle(
            x, y, x, y,  width=2, activefill=c, outline=c)  # 绘制新图
        self.area[self.areaType].append([(x, y), (x, y)])  # 向对应列表中增加1个矩形
        self.areaHistory.append({"id": id, "type": self.areaType})  # 载入历史记录

    def mouseMove(self, event):  # 鼠标拖动，刷新最后的矩形
        if self.areaType == -1:
            return
        x, y = event.x, event.y
        if x > self.imgReSize[0]:  # 防止越界
            x = self.imgReSize[0]
        elif x < 0:
            x = 0
        if y > self.imgReSize[1]:
            y = self.imgReSize[1]
        elif y < 0:
            y = 0
        x0, y0 = self.area[self.areaType][-1][0][0], self.area[self.areaType][-1][0][1]
        # 刷新历史记录中最后的图形的坐标
        self.canvas.coords(self.areaHistory[-1]["id"], x0, y0, x, y)
        self.area[self.areaType][-1][1] = (x, y)  # 刷新右下角点


# 测试
if __name__ == "__main__":
    SelectAreaWin()
