from utils.logger import GetLog
from utils.config import Config, ScsModeFlag
from utils.tool import Tool
from utils.hotkey import Hotkey  # 快捷键

# 获取显示器信息
from win32api import EnumDisplayMonitors, GetMonitorInfo
from win32gui import CreateDC
from win32print import GetDeviceCaps
# 剪贴板
from io import BytesIO
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB

import tkinter as tk
from PIL import ImageGrab, ImageTk
from enum import Enum

# TODO :
# 截图模块的工作原理是：先获取虚拟屏幕（所有显示器的画面拼凑在一起）的完整截图。然后创建一块画布，
# 画布的起点(左上角)是虚拟屏幕的左上角(xy可能为负值)，画布的宽高是虚拟屏幕的宽高，
# 然后在画布上显示完整截图，监听用户按下与拖拽。此时画布上显示的截图的位置应与真实屏幕画面一一对应。
# 但问题是，画布作为一个窗口，自身有一个缩放比例（即它出生的那块屏幕的缩放比）。
# 若多屏幕的其中某块屏幕的缩放比与画布的缩放比不一致，在一定排列下，它们的逻辑坐标会错位，表现为画面错位。
# 我原本希望通过获取全部屏幕的物理分辨率和逻辑分辨率，得到各自的缩放比，进而计算出画布坐标系下的“真实”逻辑坐标。
# 但是，我没能摸清规律。参数与太多因素相关，
# 屏幕的排列方式、软件点开时的状态、画布创建时的位置……都可能影响逻辑坐标和逻辑分辨率，
# 使得很难计算画布坐标系下应该对屏幕矫正的锚点和比例。

Log = GetLog()


def _ScreenshotClose(flag, errMsg=None):
    Log.info('截图结束')
    Config.main.closeScreenshot(flag, errMsg)


def ScreenshotCopy():
    '''截屏，保存到剪贴板，然后调用主窗的closeScreenshot接口'''
    scsMode = Config.get('scsMode').get(Config.get(
        'scsModeName'), ScsModeFlag.multi)  # 当前截屏模式
    if scsMode == ScsModeFlag.multi:  # 内置截图模式
        SSWin.startGrab()
    elif scsMode == ScsModeFlag.system:  # 系统截图模式
        SSSys.startGrab()
    else:
        _ScreenshotClose(False, '未知的截图模式！')


class ScreenshotSys():  # 系统截图模式

    def __init__(self):
        self.isInitKey = False
        self.isWorking = False
        self.checkTimeMax = 10  # 最大检查次数
        self.checkTimeRate = 10  # 检查间隔频率，毫秒
        self.checkTime = 0  # 当前剩余检查次数
        self.position = (0, 0)

    def startGrab(self):  # 启动截屏
        '''启动系统截图。若通过快捷键进入，必须为win+shift+S'''
        Tool.emptyClipboard()  # 清空剪贴板
        self.isWorking = True
        if not self.isInitKey:
            self.__initKey()
        if not Hotkey.isPressed('win'):  # 不是通过快捷键进入
            Hotkey.send('win+shift+s')  # 发送系统截图快捷键
        Log.info('系统截图启动')

    def __initKey(self):  # 初始化监听
        # 绑定全局事件
        Hotkey.addRelease(  # Esc抬起，系统截图失败
            'esc', lambda: self.__close(False))
        Hotkey.addMouseButtonDown(self.__onDown)  # 注册监听鼠标左/右按下
        Hotkey.addMouseButtonUp(self.__onUp)  # 注册监听鼠标左/右抬起
        self.isInitKey = True

    def __onDown(self, pos):  # 用户操作开始
        if self.isWorking:
            self.position = pos  # 获取鼠标当前位置

    def __onUp(self, pos):  # 用户操作结束
        if self.isWorking:
            if self.position == pos:  # 鼠标起始结束位置相同，截图失败
                self.__close(False)
                return
            self.checkTime = 0
            self.__checkClipboard()

    def __checkClipboard(self):  # 检查剪贴板中是否已存在截图
        if self.checkTime >= self.checkTimeMax:
            self.__close(False)  # 检查次数超限，截图失败
            return
        clipData = Tool.getClipboardFormat()  # 读取剪贴板
        if clipData == 2:  # 系统截图已保存到剪贴板内存，截图成功
            Log.info(f'  第{self.checkTime}次检查成功')
            self.__close(True)
            return
        Log.info(f'  第{self.checkTime}次检查')
        self.checkTime += 1
        # 定时器指定下一轮查询
        Config.main.win.after(self.checkTimeRate, self.__checkClipboard)

    def __close(self, flag=False):  # 退出
        if self.isWorking:
            Hotkey.removeMouse()  # 注销监听鼠标
            self.isInitKey = False
            self.isWorking = False
            _ScreenshotClose(flag)


SSSys = ScreenshotSys()


class _DrawMode(Enum):
    ready = 1  # 准备中
    drag = 2  # 拖拽中


class ScreenshotWin():  # 内置截图模式
    OB = -100  # 元素隐藏屏幕外的位置

    def __init__(self):
        self.isInitWin = False  # 防止重复初始化窗体
        self.isInitGrab = False  # 防止未初始化截图参数时触发事件
        self.errMsg = None  # 记录错误，传给调用者
        self.screenScaleList = None  # 记录各个屏幕分别的缩放比例
        self.promptSss = True  # 本次使用期间显示缩放提示
        self.lastScInfos = None  # 上一轮的屏幕参数

    def startGrab(self):  # 启动截屏
        '''启动区域截图'''
        # “虚拟屏幕”指多显示器画面的拼凑在一起的完整画面
        self.image = ImageGrab.grab(all_screens=True)  # 对整个虚拟屏幕截图，物理分辨率

        if not self.isInitWin:
            self.__initWin()

        self.imageResult = None  # 结果图片
        self.drawMode = _DrawMode.ready  # 准备模式
        # 获取所有屏幕的信息，提取其中的坐标信息(虚拟，非物理分辨率)
        scInfos = EnumDisplayMonitors()  # 所有屏幕的信息
        self.scBoxList = [s[2] for s in scInfos]  # 提取虚拟分辨率的信息
        # 计算缩放比例，若不一致，则发送提示弹窗
        # 条件：需要提示 | 大于一块屏幕时 | 本次信息与上次不同 | 设置需要提示
        scInfosLen = len(scInfos)
        if self.promptSss and scInfosLen > 1 and not self.lastScInfos == scInfos and Config.get('promptScreenshotScale'):
            scList = []
            self.lastScInfos = scInfos  # 屏幕信息与上次一样时跳过检测，减少耗时
            # 提取所有屏幕缩放比例
            for index, sc in enumerate(scInfos):
                # 获取设备信息字典，得到设备名称 Device
                # 物理设备信息(dict) = GetMonitorInfo(hMonitor)
                info = GetMonitorInfo(scInfos[index][0])
                # 为显示设备创建设备上下文，得到物理设备句柄 hDC
                # 设备句柄(int) = CreateDC (设备名称, 设备名称 , None )
                hDC = CreateDC(info['Device'], info['Device'], None)
                w = GetDeviceCaps(hDC, 118)  # 常量 win32con.DESKTOPHORZRES
                # h = GetDeviceCaps(hDC, 117)  # 常量 win32con.DESKTOPVERTRES
                # 得到缩放比，即windows的“更改文本、应用等项目的大小”
                s = w / (sc[2][2]-sc[2][0])
                scList.append(s)
            # 检查缩放比例是否一致
            isEQ = True
            for i in range(1, scInfosLen):
                if not abs(scList[i] - scList[0]) < 0.001:
                    isEQ = False
                    break
            # 不一致，提示
            if not isEQ:
                self.screenScaleList = scList
                msg = f'''您当前使用{scInfosLen}块屏幕，且缩放比例不一致，分别为 {scList} 。

可能导致Umi-OCR截图异常，如画面不完整、窗口变形、识别不出文字等。
若出现这种情况，
请在系统设置【更改文本、应用等项目的大小】将所有屏幕调到相同数值。
或者，请在软件设置里将截图模式切换到【Windows 系统截图】。\n'''
                Config.main.panelOutput(msg)
                Config.main.notebook.select(
                    Config.main.notebookTab[1])  # 转到输出卡
                if tk.messagebox.askyesno('提示',
                                          f'{msg}\n本次使用不再提示此消息请点击[是]，永久不再提示请点击[否]'):
                    self.promptSss = False
                else:
                    Config.set('promptScreenshotScale', False, isSave=True)
        # 计算虚拟屏幕最左上角和最右下角的坐标
        scUp, scDown, scLeft, scRight = 0, 0, 0, 0
        for s in self.scBoxList:  # 遍历所有屏幕，获取最值
            if s[0] < scLeft:  # 左边缘
                scLeft = s[0]
            if s[1] < scUp:  # 上边缘
                scUp = s[1]
            if s[2] > scRight:  # 右边缘
                scRight = s[2]
            if s[3] > scDown:  # 下边缘
                scDown = s[3]
            # 计算虚拟屏幕的宽和高
            scWidth, scHeight = scRight - scLeft, scDown - scUp
        # 多显示器处理完毕
        self.scBoxVirtual = (scLeft, scUp, scRight, scDown,
                             scWidth, scHeight)
        self.allScale = self.image.size[0] / scWidth  # 整个虚拟屏幕的缩放比例
        # 主窗口设置为铺满虚拟屏幕
        bd, bdp = 2, 1  # 边缘要额外拓展1像素，以免无法接收到鼠标在边缘的点击
        scStr = f'{scWidth+bd}x{scHeight+bd}+{scLeft-bdp}+{scUp-bdp}'
        # print(f'缩放比：{self.allScale}')
        # self.topwin.tk.call('tk', 'scaling', self.allScale/75)
        self.topwin.geometry(scStr)
        self.canvas['width'] = scWidth+bd
        self.canvas['height'] = scHeight+bd
        # 原图改物理为虚拟屏幕分辨率，转成tk格式，导入画布
        self.imageTK = ImageTk.PhotoImage(
            self.image.resize((scWidth, scHeight)))
        cimg = self.canvas.create_image(  # 底图
            bdp, bdp, anchor='nw', image=self.imageTK)
        self.canvas.lower(cimg)  # 移动到最下方

        self.topwin.deiconify()  # 显示窗口
        self.isInitGrab = True
        Log.info('初始化截图')
        self.__flash()  # 闪光
        if Config.get('isDebug'):  # 显示debug信息
            c = 2 if self.debugList else 1  # 若上一轮已显示，则调用两次以刷新
            for i in range(c):  # 否则，调用一次以打开
                self.__switchDebug()

    def __initWin(self):  # 初始化窗体
        self.isInitWin = True
        # 创建窗口
        self.topwin = tk.Toplevel()
        self.topwin.withdraw()  # 隐藏窗口
        self.topwin.overrideredirect(True)  # 无边框
        self.topwin.configure(bg='black')
        # self.topwin.attributes("-alpha", 0.8)  # 透明（调试用）
        self.topwin.attributes('-topmost', 1)  # 设置层级最前
        # 创建画布及画布元素。后创建的层级在上。
        self.canvas = tk.Canvas(self.topwin, cursor='plus', bg=None,
                                highlightthickness=0, borderwidth=0)  # 取消边框
        self.canvas.pack(fill='both')
        # 瞄准盒
        rec1 = self.canvas.create_rectangle(  # 实线底层
            self.OB, self.OB, self.OB, self.OB, outline=Config.get('scsColorBoxDown'), width=2)
        rec2 = self.canvas.create_rectangle(  # 虚线表层
            self.OB, self.OB, self.OB, self.OB, outline=Config.get('scsColorBoxUp'), width=2, dash=10)
        self.sightBox = (rec1, rec2)
        self.sightBoxXY = [self.OB, self.OB, self.OB, self.OB]  # 瞄准盒坐标
        # 瞄准线
        lineColor = Config.get('scsColorLine')
        lineW = self.canvas.create_line(  # 纵向
            self.OB, self.OB, self.OB, self.OB, fill=lineColor, width=1)
        lineH = self.canvas.create_line(  # 横向
            self.OB, self.OB, self.OB, self.OB, fill=lineColor, width=1)
        self.sightLine = (lineW, lineH)
        # debug模块
        self.debugXYBox = self.canvas.create_rectangle(  # 坐标下面的底
            self.OB, self.OB, self.OB, self.OB, fill='yellow', outline='#999', width=1)
        self.debugXYText = self.canvas.create_text(self.OB, self.OB,  # 显示坐标
                                                   font=('Microsoft YaHei', 15, 'bold'), fill='red', anchor='nw')
        self.debugList = []  # 显示屏幕信息
        # 闪光模块
        self.flashList = []  # 闪光元素
        # 绑定全局事件
        Hotkey.add('esc', self.__onClose)  # 绑定Esc退出
        Hotkey.add('ctrl+shift+alt+d', self.__switchDebug)  # 切换调试信息
        # 绑定画布事件
        self.canvas.bind(f'<Button-1>', self.__onDown)  # 左键按下
        self.canvas.bind(f'<Button-3>', self.__repaint)  # 右键按下
        self.canvas.bind(f'<ButtonRelease-1>', self.__onUp)  # 左键松开
        self.canvas.bind('<Motion>', self.__onMotion)  # 鼠标移动
        self.canvas.bind('<Enter>', self.__onMotion)  # 鼠标进入，用于初始化瞄准线
        Log.info('Umi截图启动')

    def __hideElement(self, ele, size=4):  # 隐藏一个画布元素
        # 实际上是挪到画布外
        if size == 2:
            self.canvas.coords(ele, self.OB, self.OB)
        elif size == 4:
            self.canvas.coords(ele, self.OB, self.OB, self.OB, self.OB)

    def __onDown(self, event):  # 鼠标按下
        if self.drawMode == _DrawMode.ready:  # 进入拖拽模式
            self.drawMode = _DrawMode.drag
            # 记录起始点
            self.sightBoxXY[0], self.sightBoxXY[1] = event.x, event.y
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            # 隐藏瞄准线
            for i in (0, 1):
                self.__hideElement(self.sightLine[i], 4)

    def __onUp(self, event):  # 鼠标松开
        if self.drawMode == _DrawMode.drag:  # 离开拖拽模式
            self.drawMode = _DrawMode.ready
            # 记录结束点
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            self.__createGrabImg()  # 生成剪切图像
            self.__onClose()  # 关闭窗口

    def __onMotion(self, event):  # 鼠标移动
        if self.drawMode == _DrawMode.ready:  # 准备模式，刷新瞄准线
            self.canvas.coords(self.sightLine[0],
                               0, event.y, self.scBoxVirtual[4], event.y)
            self.canvas.coords(self.sightLine[1],
                               event.x, 0, event.x, self.scBoxVirtual[5])
        elif self.drawMode == _DrawMode.drag:  # 拖拽模式，刷新瞄准盒
            self.sightBoxXY[2], self.sightBoxXY[3] = event.x, event.y
            for i in (0, 1):
                self.canvas.coords(self.sightBox[i],
                                   self.sightBoxXY[0], self.sightBoxXY[1], event.x, event.y)
        if self.debugList:
            self.canvas.coords(self.debugXYText, event.x+6, event.y+3)
            self.canvas.coords(self.debugXYBox, event.x+3,
                               event.y+3, event.x+130, event.y+28)
            # self.canvas.itemconfig(self.debugXYText, {'text':
            #                                           f'{event.x} , {event.y}'})
            self.canvas.itemconfig(self.debugXYText, {'text':
                                                      f'{event.x_root} , {event.y_root}'})

    def __repaint(self, event):  # 重绘
        Log.info('重绘')
        if self.drawMode == _DrawMode.drag:  # 已在拖拽中
            self.drawMode = _DrawMode.ready  # 退出拖拽模式
            self.sightBoxXY = [self.OB, self.OB, self.OB, self.OB]
            for i in (0, 1):  # 隐藏瞄准盒，显示瞄准线
                self.__hideElement(self.sightBox[i], 4)
            self.canvas.coords(self.sightLine[0],
                               0, event.y, self.scBoxVirtual[4], event.y)
            self.canvas.coords(self.sightLine[1],
                               event.x, 0, event.x, self.scBoxVirtual[5])
        elif self.drawMode == _DrawMode.ready:  # 还在准备中
            self.__onClose()  # 关闭

    def __createGrabImg(self):  # 创建剪切图像
        box = self.sightBoxXY
        if box[0] < 0 and box[1] < 0 and box[2] < 0 and box[3] < 0:
            pass  # 未截图
        elif box[0] == box[2] or box[1] == box[3]:
            pass  # 截图面积为0，无效
        else:
            if box[0] > box[2]:  # 若坐标错位（第二点不在第一点右下角）则交换
                box[0], box[2] = box[2], box[0]
            if box[1] > box[3]:
                box[1], box[3] = box[3], box[1]
            for i in range(4):
                box[i] *= self.allScale  # 乘上缩放比例
            self.imageResult = self.image.crop(box)

    def __onClose(self, event=None):  # 关闭窗口
        if not self.isInitGrab:
            return
        # 隐藏元素
        for i in (0, 1):
            self.__hideElement(self.sightBox[i])
            self.__hideElement(self.sightLine[i])
        self.topwin.withdraw()  # 隐藏窗口
        #  初始化参数
        self.isInitGrab = False
        self.drawMode = _DrawMode.ready
        self.errMsg = None
        flag = self.copyImage()  # 复制图像
        self.image = None  # 删除图像
        self.imageResult = None  # 删除
        _ScreenshotClose(flag, self.errMsg)

    def __flash(self):  # 边缘闪光，提示已截图
        color = 'white'
        width = 100

        def closeFlash():  # 关闭闪光
            for i in self.flashList:
                self.canvas.delete(i)
            self.flashList = []
        for box in self.scBoxList:
            p1x, p1y, p2x, p2y = box
            p1x -= self.scBoxVirtual[0]
            p2x -= self.scBoxVirtual[0]
            p1y -= self.scBoxVirtual[1]
            p2y -= self.scBoxVirtual[1]
            e = self.canvas.create_rectangle(
                p1x, p1y, p2x, p2y, outline=color, width=width)
            self.flashList.append(e)
        self.topwin.after(200, closeFlash)

    def __switchDebug(self, event=None):  # 切换显示/隐藏调试信息
        if not self.isInitGrab:
            return
        color = 'red'
        if self.debugList:  # 删除调试信息
            Config.set('isDebug', False)
            for i in self.debugList:
                self.canvas.delete(i)
            self.debugList = []
            self.__hideElement(self.debugXYBox, 4)
            self.__hideElement(self.debugXYText, 2)
        else:  # 创建调试信息
            Config.set('isDebug', True)
            for index, box in enumerate(self.scBoxList):
                p1x, p1y, p2x, p2y = box
                p1x -= self.scBoxVirtual[0]
                p2x -= self.scBoxVirtual[0]
                p1y -= self.scBoxVirtual[1]
                p2y -= self.scBoxVirtual[1]
                e = self.canvas.create_rectangle(
                    p1x, p1y, p2x, p2y, outline=color, width=3)
                self.debugList.append(e)
                e = self.canvas.create_line(
                    p1x, p1y, p2x, p2y, fill=color, width=3)
                self.debugList.append(e)
                e = self.canvas.create_line(
                    p2x, p1y, p1x, p2y, fill=color, width=3)
                self.debugList.append(e)
                # 文字提示框
                e = self.canvas.create_rectangle(
                    p1x+10, p1y+10, p1x+440, p1y+60, fill='white', width=0)
                self.debugList.append(e)
                e = self.canvas.create_text(p1x+15, p1y+15,
                                            font=('', 15, 'bold'), fill=color, anchor='nw',
                                            text=f'屏幕{index+1}: {box} | {box[2]-box[0]},{box[3]-box[1]}')
                self.debugList.append(e)
                e = self.canvas.create_text(p1x+15, p1y+43,
                                            font=('', 10, ''), fill=color, anchor='nw',
                                            text=f'按 Ctrl+Shift+Alt+D 退出调试模式')
                self.debugList.append(e)
            self.canvas.lift(self.debugXYBox)  # 移动到最上方
            self.canvas.lift(self.debugXYText)  # 移动到最上方

    def copyImage(self):
        '''复制截图到剪贴板。成功返回True，否则False'''
        if not self.imageResult:
            return False
        # 图片转字节
        output = BytesIO()
        self.imageResult.save(output, 'BMP')  # 以位图保存
        imgData = output.getvalue()[14:]  # 去除header
        output.close()
        # 写入剪贴板
        try:
            OpenClipboard()  # 打开剪贴板
            EmptyClipboard()  # 清空剪贴板
            SetClipboardData(CF_DIB, imgData)  # 写入
        except Exception as err:
            self.errMsg = f'位图无法写入剪贴板，请检测是否有其他程序正在占用。\n{err}'
            return False
        finally:
            try:
                CloseClipboard()  # 关闭
            except Exception as err:
                self.errMsg = f'无法关闭剪贴板。\n{err}'
                return False
        return True


SSWin = ScreenshotWin()

# class e:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
# self.__onDown(e(0, 0))
# self.__onUp(e(50, 20))

# 虚拟屏幕总尺寸  win32api.GetSystemMetrics
# virtualX = GetSystemMetrics(78)  # 常量 win32con.SM_CXVIRTUALSCREEN
# virtualY = GetSystemMetrics(79)  # 常量 win32con.SM_CYVIRTUALSCREEN
# print(f'虚拟尺寸：{virtualX} {virtualY}\n真实尺寸：{self.image.size}')
# print(f'总缩放比例：{self.image.size[0]/virtualX}')
