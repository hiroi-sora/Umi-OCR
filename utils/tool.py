import tkinter as tk

from win32clipboard import OpenClipboard, GetPriorityClipboardFormat, CloseClipboard, GetClipboardData


class Tool:
    CF_BITMAP = 2
    CF_HDROP = 15

    @staticmethod
    def getClipboardFormat():
        '''获取剪贴板当前值的格式\n
        若为位图，返回CF_BITMAP == [int]2 \n
        若为文件句柄，返回所有路径的元组\n
        都不是，返回None
        '''
        OpenClipboard()
        formats = [   # 允许读入的剪贴板格式：
            Tool.CF_BITMAP,       # 位图，最优先
            Tool.CF_HDROP,        # 文件列表句柄（文件管理器选中文件复制）
        ]
        try:
            OpenClipboard()  # 打开剪贴板
        except Exception as err:
            tk.messagebox.showerror(
                '遇到了亿点小问题',
                f'打开剪贴板失败：{err}')
            return None
        uFormat = GetPriorityClipboardFormat(formats)  # 获取剪贴板中第一位的格式
        reData = None
        if uFormat == Tool.CF_BITMAP:  # 位图返回标志
            reData = Tool.CF_BITMAP
        elif uFormat == Tool.CF_HDROP:  # 句柄，转成路径列表
            try:
                reData = GetClipboardData(uFormat)
            except Exception as err:
                CloseClipboard()  # 关闭剪贴板
                tk.messagebox.showerror(
                    '遇到了亿点小问题',
                    f'剪贴板获取文件句柄失败：{err}')
                return None
        # 剪贴板不存在内容，或为不支持的格式
        CloseClipboard()  # 关闭剪贴板
        return reData
