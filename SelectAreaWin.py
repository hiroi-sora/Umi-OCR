import tkinter as tk
import tkinter.messagebox
from windnd import hook_dropfiles  # 文件拖拽
from PIL import Image, ImageTk


class SelectAreaWin:
    def __init__(self, closeSendData=None, defaultPath=None):
        self.closeSendData = closeSendData  # 关闭时发送数据的接口
        # self.win = tk.Tk()
        self.win = tk.Toplevel()
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)
        self.win.title("选择区域")
        self.win.resizable(False, False)  # 禁止窗口拉伸
        self.cW = 960  # 画板尺寸
        self.cH = 540
        self.imgSize = (-1, -1)  # 图像尺寸，初次加载时生效。
        self.imgSizeText = tk.StringVar(value="未设定")
        self.area = [[], [], []]  # 存储各个矩形区域的列表
        self.areaHistory = []  # 绘图历史，撤销用
        self.areaType = -1  # 当前绘图模式
        self.areaTypeIndex = [-1, -1, -1]  # 当前绘制的矩形的序号
        self.areaColor = ["red", "green",
                          "gold1", "whitesmoke"]  # 各个矩形区域的标志颜色
        # 操作板
        tk.Frame(self.win, height=10).pack(side='top')
        ctrlFrame = tk.Frame(self.win)
        ctrlFrame.pack(side='top', fill='y')
        ctrlF0 = tk.Frame(ctrlFrame)
        ctrlF0.pack(side='left')
        tk.Label(ctrlF0, text="【图像分辨率】").pack()
        tk.Label(ctrlF0, textvariable=self.imgSizeText).pack()
        tk.Label(ctrlF0, text="不符合该尺寸的图片，将不应用以下设置。", wraplength=120).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF1 = tk.Frame(ctrlFrame)
        ctrlF1.pack(side='left')
        self.buttons = [None, None, None]
        self.buttons[0] = tk.Button(ctrlF1, text='+忽略区域 1', width=23, height=2, fg=self.areaColor[0],
                                    command=lambda: self.changeMode(0))
        self.buttons[0].pack()
        tk.Label(ctrlF1, text="一般情况下，[整体处于该区域内]的语句块将被忽略。",
                 wraplength=180).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF2 = tk.Frame(ctrlFrame)
        ctrlF2.pack(side='left')
        self.buttons[1] = tk.Button(ctrlF2, text='+识别区域', width=23, height=2, fg=self.areaColor[1],
                                    command=lambda: self.changeMode(1))
        self.buttons[1].pack()
        tk.Label(ctrlF2, text="若识别区域内存在语句块，则“忽略区域 1”失效。",
                 wraplength=180).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF3 = tk.Frame(ctrlFrame)
        ctrlF3.pack(side='left')
        self.buttons[2] = tk.Button(ctrlF3, text='+忽略区域 2', width=23, height=2, fg=self.areaColor[2],
                                    command=lambda: self.changeMode(2))
        self.buttons[2].pack()
        tk.Label(ctrlF3, text="当“忽略区域 1”失效时，“忽略区域 2”生效。",
                 wraplength=180).pack()
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        ctrlF4 = tk.Frame(ctrlFrame)
        ctrlF4.pack(side='left')
        tk.Button(ctrlF4, text='清空', width=10,
                  command=self.clearCanvas).pack()
        tk.Button(ctrlF4, text='撤销\nCtrl+Shift+z', width=10,
                  command=self.revokeCanvas).pack(pady=5)
        self.win.bind("<Control-Z>", self.revokeCanvas)  # 绑定撤销组合键，带shift
        tk.Frame(ctrlFrame, w=22).pack(side='left')
        tk.Button(ctrlFrame, text='完成', width=8,
                  command=lambda: self.onClose(False)).pack(side="left", fill="y")
        # 绘图板
        tk.Label(
            self.win, text="↓↓↓ 将任意图片拖入下方预览。然后点击按钮切换画笔，在下方用鼠标框选出想要的区域。请保证拖入的图片分辨率相同。↓↓↓", fg='gray').pack()
        self.canvas = tk.Canvas(self.win, width=self.cW, height=self.cH,
                                bg="gray", cursor="plus", borderwidth=0)
        self.canvas.bind("<Button-1>", self.mouseDown)  # 鼠标点击
        self.canvas.bind("<B1-Motion>", self.mouseMove)  # 鼠标移动
        self.canvas.pack()
        hook_dropfiles(self.win, func=self.draggedFiles)  # 注册文件拖入
        if defaultPath:  # 打开默认图片
            self.loadImage(defaultPath)

        self.win.mainloop()

    def onClose(self, isAsk=True):  # 点击关闭。isAsk为T时询问。
        data = None  # 默认不回传数据
        if self.area[0] or self.area[1] or self.area[2]:  # 数据存在
            if isAsk:  # 需要问
                if tk.messagebox.askokcancel('关闭窗口', '要应用选区吗？'):  # 需要应用
                    data = self.getData()
            else:  # 不需要问
                data = self.getData()
        if self.closeSendData:  # 通信接口存在，则回传数据
            self.closeSendData(data)
        self.win.destroy()  # 销毁窗口

    def getData(self):  # 将数据传给接口，然后关闭窗口
        area = [[], [], []]
        scale = self.imgSize[0] / self.imgReSize[0]
        for i in range(3):
            for a in self.area[i]:
                a00, a01, a10, a11 = int(
                    a[0][0]*scale), int(a[0][1]*scale), int(a[1][0]*scale), int(a[1][1]*scale)
                if a00 > a10:  # x对调
                    a00, a10 = a10, a00
                if a01 > a11:  # y对调
                    a01, a11 = a11, a01
                area[i].append([(a00, a01), (a10, a11)])
        return (self.imgSize, area)

    def draggedFiles(self, paths):  # 拖入文件
        self.loadImage(paths[0].decode("gbk"))

    def loadImage(self, path):  # 载入新图片
        """载入图片"""
        self.win.title(f"选择区域 {path}")  # 改变标题
        try:
            img = Image.open(path)
        except Exception as e:
            tk.messagebox.showwarning("图片载入失败！", e)
            return
        # 缩放图片到窗口大小
        if self.imgSize == (-1, -1):  # 初次设定
            sw, sh = self.cW/img.size[0], self.cH/img.size[1]  # 缩放比例
            if sw > sh:
                self.imgReSize = (round(img.size[0]*sh), round(img.size[1]*sh))
            else:
                self.imgReSize = (round(img.size[0]*sw), round(img.size[1]*sw))
            self.imgSize = img.size
            self.imgSizeText.set(f'{self.imgSize[0]}x{self.imgSize[1]}')
        elif not self.imgSize == img.size:  # 尺寸不符合
            tk.messagebox.showwarning("图片尺寸错误！",
                                      f"当前图像尺寸限制为{self.imgSize[0]}x{self.imgSize[1]}，不允许加载{img.size[0]}x{img.size[1]}的图片。\n若要解除限制、更改为其他分辨率，请点击“清空”后重新拖入图片。")
            return
        img = img.resize(self.imgReSize, Image.ANTIALIAS)
        # 缓存图片并显示
        self.imgFile = ImageTk.PhotoImage(img)  # 缓存图片
        imgID = self.canvas.create_image(
            0, 0, anchor='nw', image=self.imgFile)  # 绘制图片
        self.canvas.tag_lower(imgID)  # 将该元素移动到最下方，防止挡住矩形们

    def changeMode(self, type_):  # 切换绘图模式
        if self.imgSize == (-1, -1):
            return
        self.areaType = type_
        for b in self.buttons:
            b["state"] = tk.NORMAL  # 启用所有按钮
            b["bg"] = self.areaColor[3]
        self.buttons[type_]["state"] = tk.DISABLED  # 禁用刚按下的按钮
        self.buttons[type_]["bg"] = self.areaColor[type_]  # 切换背景颜色

    def clearCanvas(self):  # 清除画布
        self.win.title(f"选择区域")  # 改变标题
        self.area = [[], [], []]
        self.areaHistory = []
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
