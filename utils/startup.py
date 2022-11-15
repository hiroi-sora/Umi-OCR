# 启动方式相关设置
from utils.logger import GetLog
from utils.config import Config, Umi
from utils.asset import Asset

import os
import tkinter as tk
import winshell

Log = GetLog()


class ShortcutApi:
    '''操作快捷方式'''
    @staticmethod  # 询问是否静默启动。返回T为静默启动，F为正常显示窗口
    def askStartupNoWin(action):
        flag = not tk.messagebox.askyesno(
            '询问', f'通过{action}打开软件时，是否显示主窗口？\n\n是：正常显示主窗口\n否：静默启动，收纳到托盘区')
        if flag and not Config.get('isTray'):  # 当前配置不显示托盘，则自动启用托盘
            Config.set('isTray', True)
        return flag

    @staticmethod  # 添加
    def add(path, name, arguments=''):
        '''创建快捷方式'''
        winshell.CreateShortcut(
            Path=f'{path}\\{name}.lnk',
            Target=Umi.path,
            Description=name,
            Icon=(os.path.realpath(Asset.getPath('umiocrico')), 0),
            Arguments=arguments
        )

    @staticmethod  # 删除
    def remove(path, name):
        '''删除目标路径下所有含name的快捷方式，返回删除个数'''
        num = 0  # 成功个数
        subFiles = os.listdir(path)  # 遍历目录下所有文件
        for s in subFiles:
            if name in s and s.endswith('.lnk'):
                os.remove(path + '\\'+s)  # 删除文件
                num += 1
        return num

    @ staticmethod  # 切换
    def switch(action, path, configItem):
        '''切换快捷方式。动作名称 | 放置路径 | 设置项名称 | 成功添加时额外提示'''
        flag = Config.get(configItem)
        if flag:
            name = Umi.name
            Log.info(f'准备添加快捷方式。名称【{name}】，目标路径【{path}】')
            try:
                arguments = ''
                if ShortcutApi.askStartupNoWin(action):
                    arguments = '--no_win 1'
                ShortcutApi.add(path, name, arguments)
                tk.messagebox.showinfo('成功', f'{name} 已添加到{action}')
            except Exception as e:
                Config.set(configItem, False)
                tk.messagebox.showerror(
                    '遇到了一点小问题', f'创建快捷方式失败。请以管理员权限运行软件再重试。\n\n目标路径：{path}\n错误信息：{e}')
        else:
            name = Umi.pname  # 纯名称，无视版本号移除所有相关快捷方式
            Log.info(f'准备移除快捷方式。名称【{name}】，目标路径【{path}】')
            try:
                num = ShortcutApi.remove(path, name)
                if num == 0:
                    tk.messagebox.showinfo('提示', f'{name} 不存在{action}')
                elif num > 0:
                    tk.messagebox.showinfo(
                        '成功', f'{name} 已移除{num}个{action}')
            except Exception as e:
                tk.messagebox.showerror(
                    '遇到了一点小问题', f'删除快捷方式失败。请以管理员权限运行软件再重试。\n\n目标路径：{path}\n错误信息：{e}')
        if Config.get('isDebug'):
            os.startfile(path)  # 调试模式，打开对应文件夹


class Startup:
    '''各种启动方式'''

    @ staticmethod
    def switchAutoStartup():
        '''切换开机自启'''
        ShortcutApi.switch('开机启动项', winshell.startup(), 'isAutoStartup')

    @ staticmethod
    def switchStartMenu():
        '''切换开始菜单快捷方式'''
        ShortcutApi.switch('开始菜单', winshell.programs(), 'isStartMenu')

    @ staticmethod
    def switchDesktop():
        '''切换桌面快捷方式'''
        ShortcutApi.switch('桌面快捷方式', winshell.desktop(), 'isDesktop')
