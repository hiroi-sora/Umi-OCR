# 启动方式相关设置
from utils.config import Config, Umi

import tkinter as tk
import win32api
import win32con
import winshell


class Startup:

    RegRoot = win32con.HKEY_CURRENT_USER
    RegPath = r'Software\Microsoft\Windows\CurrentVersion\Run'
    RegFlag = win32con.KEY_ALL_ACCESS

    @staticmethod
    def _autoFind(key):
        '''寻找所有开机启动项，返回列表。不存在返回空。传入注册表key'''
        name = Umi.pname
        regList = []
        # 遍历键值
        try:
            i = 0
            while True:
                e = win32api.RegEnumValue(key, i)
                en = e[0]
                if name in en:
                    regList.append(en)
                i += 1
        except Exception as e:  # 遍历结束
            pass
        return regList

    @staticmethod
    def autoEnable():
        '''启用 开机自启'''
        try:
            key = win32api.RegOpenKey(
                Startup.RegRoot, Startup.RegPath, 0, Startup.RegFlag)
        except Exception as e:
            tk.messagebox.showerror(
                '遇到了一点小问题', f'打开注册表失败。请以管理员权限运行软件再重试。\n\n{e}')
            return
        try:
            tips = ''
            # 移除旧的启动项
            items = Startup._autoFind(key)
            if items:
                for i in items:
                    win32api.RegDeleteValue(key, i)
                tips += f'移除{len(items)}个旧的开机启动项\n\n'
            # 添加新的启动项
            name = Umi.name
            path = Umi.path
            win32api.RegSetValueEx(
                key, name, 0, win32con.REG_SZ, path)
            tips += f'添加新的开机启动项：【{name}】\n启动路径：{path}'
            tk.messagebox.showinfo('已设置开机自启', tips)
        except Exception as e:
            tk.messagebox.showerror(
                '遇到了一点小问题', f'添加开机启动项失败。请以管理员权限运行软件再重试。\n\n{e}')
        finally:
            win32api.RegCloseKey(key)

    @staticmethod
    def autoDisable():
        '''禁用 开机自启'''
        try:
            key = win32api.RegOpenKey(
                Startup.RegRoot, Startup.RegPath, 0, Startup.RegFlag)
        except Exception as e:
            tk.messagebox.showerror(
                '遇到了一点小问题', f'打开注册表失败。请以管理员权限运行软件再重试。\n\n{e}')
            return
        try:
            # 移除旧的启动项
            items = Startup._autoFind(key)
            if items:
                tips = f'移除{len(items)}个旧的开机启动项：'
                for i in items:
                    win32api.RegDeleteValue(key, i)
                    tips += f'\n{i}'
            else:
                tips = '当前没有开机启动项'
            tk.messagebox.showinfo('已禁用开机自启', tips)
        except Exception as e:
            tk.messagebox.showerror(
                '遇到了一点小问题', f'移除开机启动项失败。请以管理员权限运行软件再重试。\n\n{e}')
        finally:
            win32api.RegCloseKey(key)

    @staticmethod
    def shortcut(path):
        '''创建快捷方式'''
        try:
            spath = f'{path}\\{Umi.name}.lnk'
            starget = Umi.path
            sdesc = Umi.name
            winshell.CreateShortcut(
                Path=spath,
                Target=starget,
                Description=sdesc
            )
            return True
        except Exception as e:
            tk.messagebox.showerror(
                '遇到了一点小问题', f'创建快捷方式失败。请以管理员权限运行软件再重试。\n\n{e}')
            return False

    @staticmethod
    def shortcutDesktop():
        '''创建桌面快捷方式'''
        if Startup.shortcut(winshell.desktop()):
            tk.messagebox.showinfo('成功', 'Umi-OCR 已添加桌面快捷方式')
