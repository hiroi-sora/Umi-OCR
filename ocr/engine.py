from utils.logger import GetLog
from utils.config import Config, RunModeFlag
from ocr.api_ppocr_json import OcrAPI

import os
import time
import asyncio
import threading
from operator import eq
from enum import Enum

Log = GetLog()


class EngFlag(Enum):
    '''引擎运行状态标志'''
    none = 0  # 不在运行
    initing = 1  # 正在启动
    waiting = 2  # 待命
    running = 3  # 工作中


class MsnFlag(Enum):
    '''批量任务状态标志'''
    none = 0  # 不在运行
    initing = 1  # 正在启动
    running = 2  # 工作中
    stopping = 3  # 停止中


class OcrEngine:
    '''OCR引擎，含各种操作的方法'''

    def __init__(self):
        # self.__initVar() # 不能使用__initVar，不能调用self.setEngFlag()，因为不能保证主tk已经启动事件循环
        self.__ocrInfo = ()  # 记录之前的OCR参数
        self.__ramTips = ''  # 内存占用提示
        self.__runMissionLoop = None  # 批量识别的事件循环
        self.ocr = None  # OCR API对象
        self.winSetRunning = None
        self.engFlag = EngFlag.none
        self.msnFlag = MsnFlag.none

    def __initVar(self):
        self.__ocrInfo = ()  # 记录之前的OCR参数
        self.__ramTips = ''  # 内存占用提示
        self.ocr = None  # OCR API对象
        # self.msnFlag = MsnFlag.none  # 任务状态不能在这里改，可能引擎已经关了，任务线程还在继续

    def __setEngFlag(self, engFlag):
        '''更新引擎状态并向主窗口通知'''
        self.engFlag = engFlag
        if self.ocr and Config.get('isDebug'):
            if engFlag == EngFlag.waiting:  # 刷新内存占用
                self.__ramTips = f'（内存：{self.ocr.getRam()}）'
        msg = {
            EngFlag.none:  '已关闭',
            EngFlag.initing:  '正在启动',
            EngFlag.waiting:  f'待命{self.__ramTips}',
            EngFlag.running:  f'工作{self.__ramTips}',
        }.get(engFlag, f'未知（{engFlag}）')
        isTkUpdate = False
        if engFlag == EngFlag.initing:  # 启动中，刷新一下UI
            isTkUpdate = True
        Config.set('ocrProcessStatus', msg, isTkUpdate)  # 设置
        # Log.info(f'引擎 ⇒ {engFlag}')

    def __setMsnFlag(self, msnFlag):
        '''更新任务状态并向主窗口通知'''
        self.msnFlag = msnFlag
        if self.winSetRunning:
            self.winSetRunning(msnFlag)
        # Log.info(f'任务 ⇒ {msnFlag}')

    @staticmethod
    def __tryFunc(func, *e):
        '''尝试执行func'''
        if func:
            try:
                func(*e)
            except Exception as e:
                errMsg = f'调用函数 {str(func)} 异常： {e}'
                Log.error(errMsg)
                Config.main.panelOutput(errMsg+'\n')

    def start(self):
        '''启动引擎。若引擎已启动，且参数有更新，则重启。'''
        if self.engFlag == EngFlag.initing:  # 正在初始化中，严禁重复初始化
            return
        # 检查引擎路径
        ocrToolPath = Config.get('ocrToolPath')
        if not os.path.isfile(ocrToolPath):
            raise Exception(
                f'未在以下路径找到引擎组件\n【{ocrToolPath}】\n\n请将引擎组件【PaddleOCR-json】文件夹放置于指定路径！')
        # 获取静态参数
        ang = ' -cls=1 -use_angle_cls=1' if Config.get('isOcrAngle') else ''
        limit = f" -limit_type={Config.get('ocrLimitMode').get(Config.get('ocrLimitModeName'),'min')} -limit_side_len={Config.get('ocrLimitSize')}"
        staticArgs = f"{ang}{limit}\
 -cpu_threads={Config.get('ocrCpuThreads')}\
 -enable_mkldnn={Config.get('isOcrMkldnn')}\
 {Config.get('argsStr')}"  # 静态启动参数字符串。注意每个参数前面的空格
        # 整合最新OCR参数
        info = (
            ocrToolPath,  # 识别器路径
            Config.get('ocrConfig')[Config.get(
                'ocrConfigName')]['path'],  # 配置文件路径
            staticArgs,  # 启动参数
        )
        isUpdate = not eq(info, self.__ocrInfo)  # 检查是否有变化

        if self.ocr:  # OCR进程已启动
            if not isUpdate:  # 无变化则放假
                return
            self.stop(True)  # 有变化则先停止OCR进程再启动。传入T表示是在重启，无需中断任务。

        self.__ocrInfo = info  # 记录参数。必须在stop()之后，以免被覆盖。
        try:
            Log.info(f'启动引擎，参数：{info}')
            self.__setEngFlag(EngFlag.initing)  # 通知启动中
            self.ocr = OcrAPI(*self.__ocrInfo)  # 启动引擎
            # 检查启动引擎这段时间里，引擎有没有被叫停
            if not self.engFlag == EngFlag.initing:  # 状态被改变过了
                Log.info(f'初始化后，引擎被叫停！{self.engFlag}')
                self.stop()
                return
            self.__setEngFlag(EngFlag.waiting)  # 通知待命
        except Exception as e:
            self.stop()
            raise

    def stop(self, isRestart=False):
        '''立刻终止引擎。isRE为T时表示这是在重启，无需中断任务。'''
        if (self.msnFlag == MsnFlag.initing or self.msnFlag == MsnFlag.running)\
                and not self.engFlag == EngFlag.none and not isRestart:
            Log.info(f'引擎stop，停止任务！')
            self.__setMsnFlag(MsnFlag.stopping)  # 设任务需要停止
        if hasattr(self.ocr, 'stop'):
            self.ocr.stop()
        del self.ocr
        self.ocr = None
        self.__setEngFlag(EngFlag.none)  # 通知关闭
        self.__initVar()

    def stopByMode(self):
        '''根据配置模式决定是否停止引擎'''
        if self.msnFlag == MsnFlag.initing or self.msnFlag == MsnFlag.running\
                and not self.engFlag == EngFlag.none:
            self.__setMsnFlag(MsnFlag.stopping)  # 设任务需要停止
        n = Config.get('ocrRunModeName')
        modeDict = Config.get('ocrRunMode')
        if n in modeDict.keys():
            mode = modeDict[n]
            if mode == RunModeFlag.short:  # 按需关闭
                self.stop()

    def run(self, path):
        '''执行单张图片识别，输入路径，返回字典'''
        if not self.ocr:
            self.__setEngFlag(EngFlag.none)  # 通知关闭
            return {'code': 404, 'data': f'引擎未在运行'}
        self.__setEngFlag(EngFlag.running)  # 通知工作
        data = self.ocr.run(path)
        # 有可能因为提早停止任务或关闭软件，引擎被关闭，OCR.run提前出结果
        # 此时 engFlag 已经被主线程设为 none，如果再设waiting可能导致bug
        # 所以检测一下是否还是正常的状态 running ，没问题才通知待命
        if self.engFlag == EngFlag.running:
            self.__setEngFlag(EngFlag.waiting)  # 通知待命
        return data

    def runMission(self, paths, msn):
        '''批量识别多张图片，异步。若引擎未启动，则自动启动。\n
        paths: 路径\n
        msn:   任务器对象，Msn的派生类，必须含有 onStart|onGet|onStop|onError 四个方法'''
        if not self.msnFlag == MsnFlag.none:  # 正在运行
            Log.error(f'已有任务未结束就开始了下一轮任务')
            raise Exception('已有任务未结束')

        self.winSetRunning = Config.main.setRunning  # 设置运行状态接口
        self.__setMsnFlag(MsnFlag.initing)  # 设任务初始化

        def runLoop():  # 启动事件循环
            asyncio.set_event_loop(self.__runMissionLoop)
            self.__runMissionLoop.run_forever()

        # 在当前线程下创建事件循环
        self.__runMissionLoop = asyncio.new_event_loop()
        # 开启新的线程，在新线程中启动事件循环
        threading.Thread(target=runLoop).start()
        # 在新线程中事件循环不断游走执行
        asyncio.run_coroutine_threadsafe(self.__runMission(
            paths, msn
        ), self.__runMissionLoop)

    async def __runMission(self, paths, msn):
        '''新线程中批量识图。在这个线程里更新UI是安全的。'''

        num = {
            'all': len(paths),  # 全部数量
            'now': 1,  # 当前处理序号
            'index': 0,  # 当前下标
            'succ': 0,  # 成功个数
            'err': 0,  # 失败个数
            'exist': 0,  # 成功里面有文字的个数
            'none': 0,  # 成功里面无文字的个数
            'time': 0,  # 执行至今的总时间
            'timeNow': 0,  # 这一轮的耗时
        }

        def close():  # 停止
            try:
                self.__runMissionLoop.stop()  # 关闭异步事件循环
            except Exception as e:
                Log.error(f'任务线程 关闭任务事件循环失败： {e}')
            self.stopByMode()  # 按需关闭OCR进程
            self.__tryFunc(msn.onStop, num)
            self.__setMsnFlag(MsnFlag.none)  # 设任务停止
            Log.info(f'任务close！')

        # 启动OCR引擎，批量任务初始化 =========================
        try:
            self.start()  # 启动或刷新引擎
        except Exception as e:
            Log.error(f'批量任务启动引擎失败：{e}')
            self.__tryFunc(msn.onError, num, f'无法启动引擎：{e}')
            close()
            return
        timeStart = time.time()  # 启动时间
        timeLast = timeStart  # 上一轮结束时间

        # 检查启动引擎这段时间里，任务有没有被叫停 =========================
        if self.msnFlag == MsnFlag.stopping:  # 需要停止
            close()
            return
        # 主窗UI和任务处理器初始化 =========================
        self.__setMsnFlag(MsnFlag.running)  # 设任务运行
        self.__tryFunc(msn.onStart, num)

        # 正式开始任务 =========================
        for path in paths:
            if self.msnFlag == MsnFlag.stopping:  # 需要停止
                close()
                return
            isAddErr = False
            try:
                data = self.run(path)  # 调用图片识别
                # 刷新时间
                timeNow = time.time()  # 本轮结束时间
                num['time'] = timeNow-timeStart
                num['timeNow'] = timeNow-timeLast
                timeLast = timeNow
                # 刷新量
                if data['code'] == 100:
                    num['succ'] += 1
                    num['exist'] += 1
                elif data['code'] == 101:
                    num['succ'] += 1
                    num['none'] += 1
                else:
                    num['err'] += 1
                    isAddErr = True
                    # 若设置了进程按需关闭，中途停止任务会导致进程kill，本次识别失败
                    # 若设置了进程后台常驻，中途停止任务会让本次识别完再停止任务
                    # 这些都是正常的（设计中的）
                    # 但是，引擎进程意外关闭导致图片识别失败，则是不正常的；所以不检测engFlag
                    if self.msnFlag == MsnFlag.stopping:  # 失败由强制停止引擎导致引起
                        data['data'] = '这是正常情况。中途停止任务、关闭引擎，导致本张图片未识别完。'
                # 调用取得事件
                self.__tryFunc(msn.onGet, num, data)
            except Exception as e:
                Log.error(f'任务线程 OCR失败： {e}')
                if not isAddErr:
                    num['err'] += 1
                continue
            finally:
                num['now'] += 1
                num['index'] += 1

        close()


OCRe = OcrEngine()  # 引擎单例
