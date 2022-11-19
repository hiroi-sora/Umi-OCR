from utils.logger import GetLog

import os
import sys
import psutil  # 进程检查
import json
from enum import Enum
import tkinter as tk
import tkinter.messagebox
from locale import getdefaultlocale

Log = GetLog()


# 项目属性
class Umi:
    name = None  # 带版本号的名称
    pname = None  # 纯名称，固定
    ver = None  # 版本号
    website = None  # 主页
    about = None  # 简介
    path = os.path.realpath(sys.argv[0])  # 当前入口文件的路径
    cwd = os.path.dirname(path)  # 当前应设的工作目录


# 重设工作目录，防止开机自启丢失工作目录。此行代码必须比asset.py等模块优先执行
os.chdir(Umi.cwd)


# 枚举
class RunModeFlag(Enum):
    '''进程管理模式标志'''
    short = 0  # 按需关闭（减少空闲时内存占用）
    long = 1  # 后台常驻（大幅加快任务启动速度）


class ScsModeFlag(Enum):
    '''截屏模式标志'''
    multi = 0  # 多屏幕模式，目前仅能适配缩放比相同的多个屏幕
    system = 1  # 系统截屏模式


class ClickTrayModeFlag(Enum):
    '''点击托盘时模式标志'''
    show = 0  # 显示主面板
    screenshot = 1  # 截屏
    clipboard = 2  # 粘贴图片


class WindowTopModeFlag():
    '''窗口置顶模式标志'''
    # 不继承枚举
    never = 0  # 永不
    finish = 1  # 任务完成时置顶
    eternity = 2  # 永远保持置顶


# 配置文件路径
ConfigJsonFile = 'Umi-OCR_config.json'

# 配置项
_ConfigDict = {
    # 软件设置
    'isDebug': {  # T时Debug模式
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isAdvanced': {  # T时高级模式，显示额外的设置项
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isTray': {  # T时展示托盘图标
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    'isBackground': {  # T时点关闭进入后台运行
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'clickTrayModeName': {  # 当前选择的点击托盘图标模式名称
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'clickTrayMode': {  # 点击托盘图标模式
        'default': {
            '显示面板': ClickTrayModeFlag.show,
            '屏幕截图': ClickTrayModeFlag.screenshot,
            '粘贴图片': ClickTrayModeFlag.clipboard,
        },
        'isSave': False,
        'isTK': False,
    },
    'textpanelFontFamily': {  # 主输出面板字体
        'default': 'Microsoft YaHei UI',
        'isSave': True,
        'isTK': True,
    },
    'textpanelFontSize': {  # 主输出面板字体大小
        'default': 14,
        'isSave': True,
        'isTK': True,
    },
    'isTextpanelFontBold': {  # T时主输出面板字体加粗
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isWindowTop': {  # T时窗口置顶
        'default': False,
        'isSave': False,  # 不保存，仅作为标记
        'isTK': True,
    },
    'WindowTopMode': {  # 窗口置顶模式
        'default': WindowTopModeFlag.finish,
        'isSave': True,
        'isTK': True,
    },
    'isAutoStartup': {  # T时已添加开机自启
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isStartMenu': {  # T时已添加开始菜单
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isDesktop': {  # T时已添加桌面快捷方式
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    # 快捷识图设置
    'isHotkeyClipboard': {  # T时启用读剪贴板快捷键
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    'hotkeyClipboard': {  # 读剪贴板快捷键，字符串
        'default': 'win+alt+v',
        'isSave': True,
        'isTK': True,
    },
    'isHotkeyScreenshot': {  # T时启用截屏快捷键
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    'isScreenshotHideWindow': {  # T时截屏前隐藏窗口
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'screenshotHideWindowWaitTime': {  # 截屏隐藏窗口前等待时间
        'default': 200,
        'isSave': True,
        'isTK': False,
    },
    'hotkeyScreenshot': {  # 截屏快捷键，字符串
        'default': 'win+alt+c',
        'isSave': True,
        'isTK': True,
    },
    'hotkeyMaxTtl': {  # 组合键最长TTL（生存时间）
        'default': 2.0,
        'isSave': True,
        'isTK': True,
    },
    'isHotkeyStrict': {  # T时组合键严格判定
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'scsModeName': {  # 当前选择的截屏模式名称
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'scsMode': {  # 截屏模式
        'default': {
            'Umi-OCR 软件截图': ScsModeFlag.multi,
            'Windows 系统截图': ScsModeFlag.system,
        },
        'isSave': False,
        'isTK': False,
    },
    'scsColorLine': {  # 截屏瞄准线颜色
        'default': '#3366ff',
        'isSave': True,
        'isTK': True,
    },
    'scsColorBoxUp': {  # 截屏瞄准盒上层颜色
        'default': '#000000',
        'isSave': True,
        'isTK': True,
    },
    'scsColorBoxDown': {  # 截屏瞄准盒下层颜色
        'default': '#ffffff',
        'isSave': True,
        'isTK': True,
    },
    'isNeedCopy': {  # T时识别完成后自动复制文字
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isNeedClear': {  # T时输出前清空面板
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    # 计划任务设置
    'isOpenExplorer': {   # T时任务完成后打开资源管理器到输出目录
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isOpenOutputFile': {  # T时任务完成后打开输出文件
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isOkMission': {  # T时本次任务完成后执行指定计划任务。
        'default': False,
        'isSave': False,
        'isTK': True,
    },
    'okMissionName': {  # 当前选择的计划任务的name。
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'okMission': {  # 计划任务事件，code为cmd代码
        'default': {
            '关机':  # 取消：shutdown /a
            {'code': r'msg %username% /time:25 "Umi-OCR任务完成，将在30s后关机" & echo 关闭本窗口可取消关机 & choice /t 30 /d y /n >nul & shutdown /f /s /t 0'},
            '休眠':  # 用choice实现延时
            {'code': r'msg %username% /time:25 "Umi-OCR任务完成，将在30s后休眠" & echo 关闭本窗口可取消休眠 & choice /t 30 /d y /n >nul & shutdown /f /h'},
        },
        'isSave': True,
        'isTK': False,
    },
    # 输入文件设置
    'isRecursiveSearch': {  # T时导入文件夹将递归查找子文件夹中所有图片
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    # 输出文件设置
    'isOutputTxt': {  # T时输出内容写入txt文件
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    'isOutputSeparateTxt': {  # T时输出内容写入每个图片同名的单独txt文件
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isOutputMD': {  # T时输出内容写入md文件
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isOutputJsonl': {  # T时输出内容写入jsonl文件
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'outputFilePath': {  # 输出文件目录
        'default': '',
        'isSave': False,
        'isTK': True,
    },
    'outputFileName': {  # 输出文件名称
        'default': '',
        'isSave': False,
        'isTK': True,
    },
    # 输出格式设置
    'isIgnoreNoText': {  # T时忽略(不输出)没有文字的图片信息
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    # 文块后处理
    'tbpuName': {  # 当前选择的文块后处理
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'tbpu': {  # 文块后处理。这个参数通过 ocr\tbpu\__init__.py 导入，避免循环引用
        'default': {
            '通用': None,
        },
        'isSave': False,
        'isTK': False,
    },
    'isAreaWinAutoTbpu': {  # T时忽略区域编辑器预览文本块后处理
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    # 引擎设置
    'ocrToolPath': {  # 引擎路径
        'default': 'PaddleOCR-json/PaddleOCR_json.exe',
        'isSave': True,
        'isTK': False,
    },
    'ocrRunModeName': {  # 当前选择的进程管理策略
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'ocrRunMode': {  # 进程管理策略
        'default': {
            '后台常驻（大幅加快任务启动速度）': RunModeFlag.long,
            '按需关闭（减少空闲时内存占用）': RunModeFlag.short,
        },
        'isSave': False,
        'isTK': False,
    },
    'ocrProcessStatus': {  # 进程运行状态字符串，由引擎单例传到tk窗口
        'default': '未启动',
        'isSave': False,
        'isTK': True,
    },
    'ocrConfigName': {  # 当前选择的配置文件的name
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'ocrConfig': {  # 配置文件信息
        'default': {  # 配置文件信息
            '简体中文': {
                'path': 'PaddleOCR_json_config_ch.txt'
            }
        },
        'isSave': True,
        'isTK': False,
    },
    'argsStr': {  # 启动参数字符串
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'isOcrAngle': {  # T时启用cls
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'ocrCpuThreads': {  # CPU线程数
        'default': 10,
        'isSave': True,
        'isTK': True,
    },
    'isOcrMkldnn': {  # 启用mkldnn加速
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    'ocrLimitModeName': {  # 当前选择的压缩限制模式的name
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'ocrLimitMode': {  # 压缩限制模式
        'default': {
            '长边压缩模式': 'max',
            '短边扩大模式': 'min',
        },
        'isSave': False,
        'isTK': False,
    },
    'ocrLimitSize': {  # 压缩阈值
        'default': 960,
        'isSave': True,
        'isTK': True,
    },
    'imageSuffix': {  # 图片后缀
        'default': '.jpg .jpe .jpeg .jfif .png .webp .bmp .tif .tiff',
        'isSave': True,
        'isTK': True,
    },
    # 更改语言窗口
    'isLanguageWinAutoExit': {  # T时语言窗口自动关闭
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isLanguageWinAutoOcr': {  # T时语言窗口修改后重复任务
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    # 防止多开相关
    'processID':  {  # 正在运行的进程的PID
        'default': -1,
        'isSave': True,
        'isTK': False,
    },
    'processKey':  {  # 可标识一个进程的信息，如进程名或路径
        'default': '',
        'isSave': True,
        'isTK': False,
    },

    # 记录不再提示
    'promptScreenshotScale':  {  # 截图时比例不对
        'default': True,
        'isSave': True,
        'isTK': False,
    },
    'promptMultiOpen':  {  # 多开提示
        'default': True,
        'isSave': True,
        'isTK': False,
    },

    # 不同模块交流的接口
    'ignoreArea':  {  # 忽略区域
        'default': None,
        'isSave': False,
        'isTK': False,
    },
    'tipsTop1': {  # 主窗口顶部进度条上方的label，左侧
        'default': '',
        'isTK': True,
    },
    'tipsTop2': {  # 主窗口顶部进度条上方的label，右侧
        'default': '拖入图片或快捷截图',
        'isTK': True,
    },
}


class ConfigModule:
    # ↓ 在这些编码下能使用全部功能，其它编码不保证能使用如拖入含中文路径的图片等功能。
    # ↓ 但识图功能是可以正常使用的。
    __sysEncodingSafe = ['cp936', 'cp65001']

    __tkSaveTime = 200  # tk变量改变多长时间后写入本地。毫秒

    # ==================== 初始化 ====================

    def __init__(self):
        self.main = None  # win_main的self，可用来获取主it刷新界面或创建计时器
        self.sysEncoding = 'ascii'  # 系统编码。初始化时获取
        self.__saveTimer = None  # 计时器，用来更新tk变量一段时间后写入本地
        self.__optDict = {}  # 配置项的数据
        self.__tkDict = {}  # tk绑定变量
        self.__saveList = []  # 需要保存的项
        self.__traceDict = {}  # 跟踪值改变
        # 将配置项加载到self
        for key in _ConfigDict:
            value = _ConfigDict[key]
            self.__optDict[key] = value['default']
            if value.get('isSave', False):
                self.__saveList.append(key)
            if value.get('isTK', False):
                self.__tkDict[key] = None

    def initTK(self, main):
        '''初始化tk变量'''
        self.main = main  # 主窗口

        def toSaveConfig():  # 保存值的事件
            self.save()
            self.__saveTimer = None

        def onTkVarChange(key):  # 值改变的事件
            self.update(key)  # 更新配置项
            if key in self.__saveList:  # 需要保存
                if self.__saveTimer:  # 计时器已存在，则停止已存在的
                    self.main.win.after_cancel(self.__saveTimer)  # 取消计时
                    self.__saveTimer = None
                self.__saveTimer = self.main.win.after(  # 重新计时
                    self.__tkSaveTime, toSaveConfig)

        for key in self.__tkDict:
            if isinstance(self.__optDict[key], bool):  # 布尔最优先，以免被int覆盖
                self.__tkDict[key] = tk.BooleanVar()
            elif isinstance(self.__optDict[key], str):
                self.__tkDict[key] = tk.StringVar()
            elif isinstance(self.__optDict[key], float):
                self.__tkDict[key] = tk.DoubleVar()
            elif isinstance(self.__optDict[key], int):
                self.__tkDict[key] = tk.IntVar()
            else:  # 给开发者提醒
                raise Exception(f'配置项{key}要生成tk变量，但类型不合法！')
            # 赋予初值
            self.__tkDict[key].set(self.__optDict[key])
            # 跟踪值改变事件
            self.__tkDict[key].trace(
                "w", lambda *e, key=key: onTkVarChange(key))

    # ==================== 读写本地文件 ====================

    def load(self):
        '''从本地json文件读取配置。必须在initTK后执行'''

        # 初始化编码，获取系统编码
        # https://docs.python.org/zh-cn/3.8/library/locale.html#locale.getdefaultlocale
        # https://docs.python.org/zh-cn/3.8/library/codecs.html#standard-encodings
        syse = getdefaultlocale()[1]
        if syse:
            self.sysEncoding = syse

        try:
            with open(ConfigJsonFile, 'r', encoding='utf8')as fp:
                jsonData = json.load(fp)  # 读取json文件
                for key in jsonData:
                    if key in self.__optDict:
                        self.set(key, jsonData[key])
        except json.JSONDecodeError:  # 反序列化json错误
            if tk.messagebox.askyesno(
                '遇到了一点小问题',
                    f'配置文件 {ConfigJsonFile} 格式错误。\n\n【是】 重置该文件\n【否】 退出本次运行'):
                self.save()
            else:
                os._exit(0)
        except FileNotFoundError:  # 无配置文件
            # 当成是首次启动软件，提示
            if self.sysEncoding not in self.__sysEncodingSafe:  # 不安全的地区
                tk.messagebox.showwarning(
                    '警告',
                    f'您的系统地区语言编码为[{self.sysEncoding}]，可能导致拖入图片的功能异常，建议使用浏览按钮导入图片。其它功能不受影响。')
            self.save()

    def checkMultiOpen(self):
        '''检查多开'''
        def isMultiOpen():
            '''主进程多开时返回T'''
            def getProcessKey(pid):
                # 区分不同时间和空间上同一个进程的识别信息
                try:
                    return str(psutil.Process(pid).create_time())
                except psutil.NoSuchProcess as e:  # 虽然psutil.pid_exists验证pid存在，但 Process 无法生成对象
                    return ''
            # 检查上次记录的pid和key是否还在运行
            lastPID = self.get('processID')
            lastKey = self.get('processKey')
            if psutil.pid_exists(lastPID):  # 上次记录的pid如今存在
                runningKey = getProcessKey(lastPID)
                if lastKey == runningKey:  # 上次记录的key与它pid当前key对应，则证实多开
                    Log.info(f'检查到进程已在运行。pid：{lastPID}，key：{lastKey}')
                    if tk.messagebox.askyesno(
                        '提示',
                            f'Umi-OCR 已在运行。\n\n【是】 退出本次运行\n【否】 多开软件'):
                        os._exit(0)
                    else:  # 忽视警告继续多开，不记录当前信息
                        return
            # 本次为唯一的进程，记录当前进程信息
            nowPid = os.getpid()
            nowKey = getProcessKey(nowPid)
            self.set('processID', nowPid)
            self.set('processKey', nowKey, isSave=True)
        if self.get('promptMultiOpen'):
            isMultiOpen()

    def save(self):
        '''保存配置到本地json文件'''
        saveDict = {}  # 提取需要保存的项
        for key in self.__saveList:
            saveDict[key] = self.__optDict[key]
        with open(ConfigJsonFile, 'w', encoding='utf8')as fp:
            fp.write(json.dumps(saveDict, indent=4, ensure_ascii=False))

    # ==================== 操作变量 ====================

    def update(self, key):
        '''更新某个值，从tk变量读取到配置项'''
        try:
            self.__optDict[key] = self.__tkDict[key].get()
        except Exception as err:
            Log.error(f'设置项{key}刷新失败：\n{err}')
        if key in self.__traceDict:
            try:
                self.__traceDict[key]()
            except Exception as err:
                Log.error(f'设置项{key}跟踪事件调用失败：\n{err}')

    def get(self, key):
        '''获取一个配置项的值'''
        return self.__optDict[key]

    def set(self, key, value, isUpdateTK=False, isSave=False):
        '''设置一个配置项的值。isSave表示非tk配置项立刻保存本地（需要先在_ConfigDict里设）'''
        if key in self.__tkDict:  # 若是tk，则通过tk的update事件去更新optDict值
            self.__tkDict[key].set(value)
            if isUpdateTK:  # 需要刷新界面
                self.main.win.update()
        else:  # 不是tk，直接更新optDict
            self.__optDict[key] = value
            if isSave and _ConfigDict[key].get('isSave', False):
                self.save()  # 保存本地

    def getTK(self, key):
        '''获取一个TK变量'''
        return self.__tkDict[key]

    def addTrace(self, key, func):
        '''跟踪一个变量，值改变时调用函数。同一个值只能注册一个函数'''
        self.__traceDict[key] = func


Config = ConfigModule()  # 设置模块 单例
