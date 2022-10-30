# 小组件
from utils.config import Config
from utils.logger import GetLog
from utils.hotkey import Hotkey  # 快捷键

import tkinter as tk
from tkinter import ttk

Log = GetLog()


class Widget:

    @staticmethod
    def comboboxFrame(master, name, configDictName, lockWidget=None, width=None):
        '''添加一个复选框框架
        父框架 | 模式名称(描述) | 模式在Config中的名称 | 锁定列表'''
        cFrame = tk.Frame(master)
        cFrame.grid_columnconfigure(1, weight=1)
        tk.Label(cFrame, text=name).grid(column=0, row=0, sticky='w')

        modeName = f'{configDictName}Name'
        modeDict = Config.get(configDictName)
        modeNameList = [i for i in modeDict]
        cbox = ttk.Combobox(cFrame, state='readonly', width=width,
                            textvariable=Config.getTK(modeName), value=modeNameList)
        cbox.grid(column=1, row=0,  sticky='ew')
        if Config.get(modeName) not in modeNameList:
            cbox.current(0)  # 初始化Combobox和configName
        if lockWidget:  # 添加到锁定列表
            lockWidget.append(  # 正常状态为特殊值
                {'widget': cbox, 'stateOFnormal': 'readonly'})
        return cFrame

    @staticmethod
    def delHotkey(hotkey):  # 移除已有快捷键
        if hotkey == '':
            return
        try:
            Hotkey.remove(hotkey)  # 移除该快捷键
        except Exception as err:  # 影响不大。未注册过就调用移除 会报这个异常
            Log.info(f'快捷键【{hotkey}】移除错误：{err}')

    @staticmethod
    def hotkeyFrame(master, name, configName, func, isFix=False, hotkeyCom=None, isAutoBind=False):
        '''添加一个热键框架
        父框架 | 热键名称(描述) | 热键在Config中的名称 | 触发事件 | 
        固定热键 | 固定热键名 | 是否创建完成后自动绑定'''

        isHotkey = f'isHotkey{configName}'
        hotkeyName = f'hotkey{configName}'

        def addHotkey(hotkey):  # 注册新快捷键
            if hotkey == '':
                Config.set(isHotkey, False)
                tk.messagebox.showwarning(
                    '提示', f'请先录制{name}快捷键')
                return
            try:
                Hotkey.add(hotkey, func)  # 添加快捷键监听
            except ValueError as err:
                Config.set(isHotkey, False)
                Config.set(hotkeyName, '')
                tk.messagebox.showwarning(
                    '提示', f'无法注册快捷键【{hotkey}】\n\n错误信息：\n{err}')

        def onRead():  # 当 修改键按下

            def readSucc(hotkey, errmsg=''):  # 录制成功的回调
                # 显示按钮
                tips.grid()
                btn.grid()
                tips2.grid_remove()
                # 失败
                if not hotkey:
                    if isUsing:  # 注册回旧按键
                        addHotkey(oldHotkey)
                    tk.messagebox.showwarning(
                        '提示', f'无法修改快捷键\n\n错误信息：\n{errmsg}')
                    return
                # 检查并注册热键
                if 'esc' in hotkey or hotkey == oldHotkey:  # ESC为取消
                    if isUsing:  # 注册回旧按键
                        addHotkey(oldHotkey)
                    return
                if isUsing:  # 需要注册新按键
                    addHotkey(hotkey)
                Config.set(hotkeyName, hotkey)  # 写入设置
                Log.info(
                    f'快捷键【{name}】修改为【{Config.get(hotkeyName)}】')

            tips.grid_remove()
            btn.grid_remove()  # 移除按钮
            tips2.grid()  # 显示提示
            hFrame.update()  # 刷新UI
            isUsing = Config.get(isHotkey)
            oldHotkey = Config.get(hotkeyName)
            if isUsing:  # 已经注册了
                Widget.delHotkey(oldHotkey)  # 先注销已有按键
            Hotkey.read(readSucc)  # 录制快捷键

        def onCheck():  # 当 复选框按下
            if isFix:
                hotkey = hotkeyCom
            else:
                hotkey = Config.get(hotkeyName)
            if Config.get(isHotkey):  # 需要注册
                addHotkey(hotkey)  # 注册按键
            else:  # 需要注销
                Widget.delHotkey(hotkey)  # 注销按键

        hFrame = tk.Frame(master)
        hFrame.grid_columnconfigure(2, weight=1)

        # 标题 | 快捷键Label | 修改
        wid = ttk.Checkbutton(hFrame, variable=Config.getTK(isHotkey),
                              text=f'{name} 快捷键　', command=onCheck)
        wid.grid(column=0, row=0, sticky='w')

        if isFix:  # 固定组合，不给修改
            tk.Label(hFrame, text='修改', fg='gray').grid(
                column=1, row=0, sticky='w')
            tips = tk.Label(hFrame, text=hotkeyCom, justify='center')
            tips.grid(column=2, row=0, sticky="nsew")
        else:  # 允许自定义修改
            btn = tk.Label(hFrame, text='修改', cursor='hand2', fg='blue')
            btn.grid(column=1, row=0, sticky='w')
            btn.bind('<Button-1>', lambda *e: onRead())
            tips = tk.Label(hFrame, textvariable=Config.getTK(hotkeyName),
                            justify='center')
            tips.grid(column=2, row=0, sticky="nsew")
        tips2 = tk.Label(hFrame, text='等待输入…… (按Esc取消)',
                         justify='center', fg='deeppink')
        tips2.grid(column=2, row=0, sticky="nsew")
        tips2.grid_remove()  # 隐藏

        # 初始注册
        if isAutoBind and Config.get(isHotkey):  # 需要注册
            addHotkey(Config.get(hotkeyName))  # 注册按键

        return hFrame
