# 截图展示

import win32api
import win32con

from utils.config import Config
from utils.asset import Asset  # 资源
from ui.win_notify import Notify

import time
import tkinter as tk
from PIL import Image, ImageTk
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB
from io import BytesIO


class ShowImage:
    def __init__(self, imgPIL=None, imgData=None):
        # imgPIL：PIL对象，imgData：位图数据。传入一个即可
        self.img, self.imgData = imgPIL, imgData
        if not self.imgData and not self.img:
            return
        if not self.imgData:  # 从PIL Image对象创建位图数据
            output = BytesIO()
            imgPIL.save(output, 'BMP')  # 以位图保存
            self.imgData = output.getvalue()[14:]  # 去除header
            output.close()
        if not self.img:  # 从位图数据创建PIL Image对象
            self.img = Image.open(BytesIO(imgData))

        # 创建Tkinter窗口
        self.win = tk.Toplevel()
        self.win.iconphoto(False, Asset.getImgTK('umiocr24'))  # 设置窗口图标
        self.win.overrideredirect(True)
        # 设置窗口大小
        self.ratio = self.img.width / self.img.height
        self.w, self.h = self.img.width, self.img.height
        hPlus = 20  # 标题栏等所占的高度
        if self.w > self.win.winfo_screenwidth():  # 防止超大
            self.w = self.win.winfo_screenwidth()
            self.h = int(self.w/self.ratio)
        if self.h > self.win.winfo_screenheight()-hPlus:
            self.h = self.win.winfo_screenheight()-hPlus
            self.w = int(self.h*self.ratio)
        self.win.geometry(f'{self.w}x{self.h+hPlus}')  # 高度+hPlus
        # 菜单栏
        self.menubar = tk.Menu(self.win)
        self.win.config(menu=self.menubar)
        self.menubar.add_command(label='　置顶', command=self._gotoTop)
        self.menubar.add_command(label='识别', command=self._ocr)
        self.menubar.add_command(label='保存', command=self._saveImage)
        # self.menubar.add_command(label='复制', command=self.copyImage)
        submenu = tk.Menu(self.menubar, tearoff=False)
        submenu.add_command(label='窗口置顶：Ctrl+T', command=self._gotoTop)
        submenu.add_command(label='文字识别：回车', command=self._ocr)
        submenu.add_command(label='保存图片到本地：Ctrl+S', command=self._saveImage)
        submenu.add_command(label='复制图片到剪贴板：Ctrl+C', command=self._copyImage)
        submenu.add_command(label='关闭窗口：Esc', command=self._onClose)
        self.menubar.add_cascade(label='更多', menu=submenu)
        # 创建Canvas对象并将其填充为整个窗口
        self.canvas = tk.Canvas(self.win, width=self.img.width, height=self.img.height, borderwidth=1,
                                relief='solid')
        self.canvas.pack(fill='both', expand=True)
        self.photo = ImageTk.PhotoImage(self.img)  # 保存图片对象
        # 在Canvas上创建图像
        self.canvas_image = self.canvas.create_image(
            0, 0, anchor='nw', image=self.photo)
        # 坐标计算
        # 窗口坐标系相对于屏幕坐标系win_cs,左上,右下
        self.w_new_x, self.w_new_y = self.win.winfo_x(), self.win.winfo_y()
        self.new_width, self.new_height = self.img.width, self.img.height
        self.ratio = self.new_width / self.new_height  # 保持缩放
        self.init_win_cs = self.w_new_x, self.w_new_y, self.w_new_x + self.new_width, self.w_new_y + self.new_height
        self.win_cs = self.init_win_cs  # 更新的
        # canvas坐标系canvas_cs左上(0,0),右下尺寸
        self.c_new_x, self.c_new_y = 0, 0
        # 事件绑定
        self.canvas.bind('<Motion>', self._on_mouse_motion)  # 绑定鼠标划过事件
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)  # 绑定鼠标左键点击事件
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)  # 绑定鼠标左键拖拽事件
        self.win.bind('<Return>', self._ocr)
        self.win.bind('<Control-t>', self._gotoTop)
        self.win.bind('<Control-s>', self._saveImage)
        self.win.bind('<Control-c>', self._copyImage)
        self.win.bind('<Escape>', self._onClose)
        # 其他初始值
        self.sum_x = 0
        self.sum_y = 0
        self.draggable = False  # 设置为可拖拽
        self.resize_mode = 0  # 总共8个位置按先天八卦顺序，默认不可调整为0
        # 窗口属性
        self.isWindowTop = False
        if Config.get('isWindowTop'):  # 初始置顶
            self._gotoTop()
        self.win.after(200, lambda: self.win.focus())  # 窗口获得焦点

    def _on_mouse_press(self, event):
        """鼠标左键按下事件，捕捉更新坐标"""
        self.c_new_x = event.x
        self.c_new_y = event.y
        self.win_cs = self.win.winfo_x(), self.win.winfo_y(), self.win.winfo_x() + self.win.winfo_width(), self.win.winfo_y() + self.win.winfo_height()
        self.sum_x = 0
        self.sum_y = 0

    def _on_mouse_drag(self, event):
        # 核心求解右上角实际坐标，及长宽尺寸
        w_x1, w_y1, w_x2, w_y2 = self.win_cs
        w_angle_1, w_angle_2, w_angle_3, w_angle_4 = [w_x1, w_y1], [w_x2, w_y1], [w_x2, w_y2], [w_x1, w_y2]  # tk中四角坐标
        print(self.c_new_x, self.c_new_y)
        # 累计拖拽或拉伸前后移动的x,y距离
        self.sum_x = self.sum_x + event.x - self.c_new_x
        self.sum_y = self.sum_y + event.y - self.c_new_y
        print("累计距离", self.sum_x, self.sum_y)
        self.win.config(cursor="none")
        if self.draggable:
            """窗口移动事件"""
            # 更新窗口位置
            self.win.config(cursor="")
            self.w_new_x = w_angle_1[0] + self.sum_x
            self.w_new_y = w_angle_1[1] + self.sum_y
            self.win.geometry(f"{self.new_width}x{self.new_height}+{self.w_new_x}+{self.w_new_y}")
        else:
            win32api.SetCursor(win32api.LoadCursor(0, self.cursor_dict[self.resize_mode if self.resize_mode else 0]))
            if self.resize_mode == 1 or self.resize_mode == 5:
                # 左下角不变
                if self.resize_mode == 1:
                    win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_SIZENS))
                else:
                    win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_SIZENESW))
                self.w_new_x = w_angle_1[0]
                self.w_new_y = w_angle_1[1] + self.sum_y
                self.new_height = abs(w_angle_4[1] - self.w_new_y)
                self.new_width = int(self.new_height * self.ratio)
                self.win.geometry(f"{self.new_width}x{self.new_height}+{self.w_new_x}+{self.w_new_y}")
            elif self.resize_mode == 2:
                # 右下角不变
                win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_SIZENWSE))
                self.w_new_y = w_angle_1[1] + self.sum_y
                self.new_height = abs(w_angle_3[1] - self.w_new_y)
                self.new_width = int(self.new_height * self.ratio)
                self.w_new_x = w_angle_3[0] - self.new_width
                self.win.geometry(f"{self.new_width}x{self.new_height}+{self.w_new_x}+{self.w_new_y}")
            elif self.resize_mode == 3 or self.resize_mode == 4:
                # 右上角不变
                self.w_new_x = w_angle_1[0] + self.sum_x
                self.w_new_y = w_angle_2[1]
                self.new_width = abs(self.w_new_x - w_angle_2[0])
                self.new_height = int(self.new_width / self.ratio)
                self.win.geometry(f"{self.new_width}x{self.new_height}+{self.w_new_x}+{self.w_new_y}")
            elif self.resize_mode == 8:
                # 左上角不变
                self.w_new_x = w_angle_1[0]
                self.w_new_y = w_angle_1[1]
                self.new_height = abs(event.y - self.c_new_y + w_angle_4[1] - w_angle_1[1])
                self.new_width = int(self.new_height * self.ratio)
                self.win.geometry(f"{self.new_width}x{self.new_height}+{self.w_new_x}+{self.w_new_y}")
            elif self.resize_mode == 6 or self.resize_mode == 7:
                # 左上角不变
                self.w_new_x = w_angle_1[0]
                self.w_new_y = w_angle_1[1]
                self.new_width = abs(event.x - self.c_new_x + w_angle_2[0] - w_angle_1[0])
                self.new_height = int(self.new_width / self.ratio)
                self.win.geometry(f"{self.new_width}x{self.new_height}+{self.w_new_x}+{self.w_new_y}")
            else:
                print("不调整大小")
        resized_img = self.img.resize(
            (self.new_width, self.new_height), Image.ANTIALIAS)
        # 将PIL Image对象转换为Tkinter PhotoImage对象，并更新Canvas上的图像
        self.photo = ImageTk.PhotoImage(resized_img)
        self.canvas.itemconfigure(self.canvas_image, image=self.photo)

    def _on_mouse_motion(self, event):
        x = event.x
        y = event.y
        x1, y1, x2, y2 = 0, 0, self.win.winfo_width(), self.win.winfo_height()
        print('x1:', x1, 'y1:', y1, 'x2:', x2, 'y2:', y2)
        m_area = 10
        self.cursor_dict, self.resize_mode, self.draggable = self.show_cursor(x, y, x1, y1, x2, y2, m_area)

    def show_cursor(self, x, y, x1, y1, x2, y2, m_area):
        """根据鼠标位置在窗口边缘显示不同的光标"""
        # 默认无操作
        resize_mode = 0
        draggable = False
        cursor_dict = {
            1: win32con.IDC_SIZENS, 2: win32con.IDC_SIZENWSE, 3: win32con.IDC_SIZEWE,
            4: win32con.IDC_SIZENESW, 5: win32con.IDC_SIZENESW, 6: win32con.IDC_SIZEWE,
            7: win32con.IDC_SIZENWSE, 8: win32con.IDC_SIZENS, 0: win32con.IDC_ARROW
        }  # 按照八卦顺序排序，乾一、兑二、离三、震四、巽五、坎六、艮七、坤八
        # 判断鼠标位置
        if x1 + m_area <= x <= x2 - m_area:
            if y1 + m_area < y < y2 - m_area:
                draggable = True
            elif y1 - m_area <= y <= y1 + m_area:
                resize_mode = 1
            elif y2 - m_area <= y <= y2 + m_area:
                resize_mode = 8
        elif x1 - m_area < x < x1 + m_area:
            if y1 - m_area < y < y1 + m_area:
                resize_mode = 2
            elif y1 + m_area <= y <= y2 - m_area:
                resize_mode = 3
            elif y2 - m_area < y < y2 + m_area:
                resize_mode = 4
        elif x2 - m_area < x < x2 + m_area:
            if y1 - m_area < y < y1 + m_area:
                resize_mode = 5
            elif y1 + m_area <= y <= y2 - m_area:
                resize_mode = 6
            elif y2 - m_area < y < y2 + m_area:
                resize_mode = 7
        # 设置光标
        win32api.SetCursor(win32api.LoadCursor(0, cursor_dict[resize_mode if resize_mode else 0]))
        return cursor_dict, resize_mode, draggable

    def _gotoTop(self, event=None):
        self.isWindowTop = not self.isWindowTop
        if self.isWindowTop:  # 启用置顶
            self.menubar.entryconfigure(1, label='已置顶')
            self.win.attributes('-topmost', 1)
        else:
            self.menubar.entryconfigure(1, label='　置顶')
            self.win.attributes('-topmost', 0)

    def _ocr(self, event=None):
        self._copyImage()
        Config.main.runClipboard()

    def _saveImage(self, event=None):
        # 打开文件选择对话框
        now = time.strftime("%Y-%m-%d %H%M%S", time.localtime())
        defaultFileName = f'屏幕截图 {now}.png'
        filePath = tk.filedialog.asksaveasfilename(
            initialfile=defaultFileName,
            defaultextension='.png',
            filetypes=[('PNG Image', '*.png')],
            title='保存图片'
        )

        if filePath:
            # 将 PIL.Image 对象保存为 PNG 文件
            self.img.save(filePath, format='PNG')

    def _copyImage(self, event=None):
        try:
            OpenClipboard()  # 打开剪贴板
            EmptyClipboard()  # 清空剪贴板
            SetClipboardData(CF_DIB, self.imgData)  # 写入
        except Exception as err:
            Notify('位图无法写入剪贴板', f'{err}')
        finally:
            try:
                CloseClipboard()  # 关闭
            except Exception as err:
                Notify('无法关闭剪贴板', f'{err}')

    def _onClose(self, event=None):
        self.photo = None  # 删除图片对象，释放内存
        self.win.destroy()  # 关闭窗口
