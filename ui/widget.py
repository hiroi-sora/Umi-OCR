# 小组件
from utils.config import Config
from utils.logger import GetLog

import tkinter as tk
import keyboard  # 绑定快捷键

Log = GetLog()


class Widget:
    @staticmethod
    def hotkeyFrame(master, name, configName, func):
        '''添加一个热键框架
        父框架 | 热键名称(描述) | 热键在Config中的名称 | 触发事件'''

        isHotkey = f'isHotkey{configName}'
        hotkeyName = f'hotkey{configName}'

        def addHotkey(hotkey):  # 注册新快捷键
            if hotkey == '':
                Config.set(isHotkey, False)
                tk.messagebox.showwarning("提示",
                                          f"请先录制{name}快捷键")
                return
            try:
                # 添加新的快捷键。suppress=True 捕获到快捷键后，阻止其继续向别的软件下发
                keyboard.add_hotkey(hotkey, func, suppress=False)
                Log.info(f'快捷键【{hotkey}】注册成功')
            except ValueError as err:
                Config.set(isHotkey, False)
                Config.set(hotkeyName, '')
                tk.messagebox.showwarning("提示",
                                          f"无法注册快捷键【{hotkey}】[{hotkey}]\n\n错误信息：\n{err}")

        def delHotkey(hotkey):  # 移除已有快捷键
            if hotkey == '':
                return
            try:
                keyboard.remove_hotkey(hotkey)  # 移除该快捷键
                Log.info(f'快捷键【{hotkey}】注销成功')
            except Exception as err:  # 影响不大。未注册过就调用移除 会报这个异常
                Log.info(f'快捷键【{hotkey}】移除错误：{err}')
                pass

        def onRead():  # 当 录制键按下
            tips.grid_remove()
            tips2.grid()  # 显示提示
            hFrame.update()  # 刷新UI
            hotkey = keyboard.read_hotkey(suppress=False)
            tips.grid()  # 显示按键
            tips2.grid_remove()
            if hotkey == "esc":  # ESC为取消
                return
            oldHotkey = Config.get(hotkeyName)
            if hotkey == oldHotkey:  # 新旧快捷键一样
                return
            if Config.get(isHotkey):  # 当前是被注册状态
                delHotkey(oldHotkey)  # 注销旧按键
                addHotkey(hotkey)  # 注册新按键
            Config.set(hotkeyName, hotkey)  # 写入设置
            Log.info(
                f'快捷键【{name}】录制为【{Config.get(hotkeyName)}】')

        def onCheck():  # 当 复选框按下
            hotkey = Config.get(hotkeyName)
            if Config.get(isHotkey):  # 需要注册
                addHotkey(hotkey)  # 注册按键
            else:  # 需要注销
                delHotkey(hotkey)  # 注销按键

        hFrame = tk.Frame(master)
        hFrame.pack(side='top', fill='x', padx=5)
        hFrame.grid_columnconfigure(2, weight=1)

        # 标题 | 快捷键Label | 录制
        wid = tk.Checkbutton(hFrame, variable=Config.getTK(isHotkey),
                             text=f'{name} 快捷键 ', command=onCheck)
        wid.grid(column=0, row=0, sticky="w")

        btn = tk.Label(hFrame, text='录制', cursor='hand2', fg='blue')
        btn.grid(column=1, row=0, sticky="w")
        btn.bind('<Button-1>', lambda *e: onRead())

        tips = tk.Label(hFrame, textvariable=Config.getTK(hotkeyName),
                        justify='center')
        tips.grid(column=2, row=0, sticky="nsew")
        tips2 = tk.Label(hFrame, text='等待输入……(Esc取消)', justify='center')
        tips2.grid(column=2, row=0, sticky="nsew")
        tips2.grid_remove()  # 隐藏

        # 初始注册
        if Config.get(isHotkey):  # 需要注册
            addHotkey(Config.get(hotkeyName))  # 注册按键

        return hFrame
