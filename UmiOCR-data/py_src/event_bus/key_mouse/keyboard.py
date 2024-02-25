from pynput import keyboard
from PySide2.QtCore import QMutex
from time import time

from ...platform import Platform
from ..pubsub_service import PubSubService


# 按键转换器
class _KeyTranslator:
    # 回调函数的 KeyCode 类型 转为键名字符串
    @staticmethod
    def key2name(key):
        return Platform.getKeyName(key)

    # 键名字符串 转为KeyCode
    @staticmethod
    def name2key(char):
        if hasattr(keyboard.Key, char):  # 控制键返回Code
            return getattr(keyboard.Key, char).value
        else:  # 非控制键返回自己
            return char

    # 多个键名的字符串 转为集合
    @staticmethod
    def names2set(char):
        return set(char.split("+"))

    # 集合转键名
    def set2names(keys):
        keys = keys.copy()
        # 优先级键名
        highPriority = ("win", "cmd", "shift", "ctrl", "alt")
        names = ""
        # 添加高优先级键
        for h in highPriority:
            if h in keys:
                if names != "":
                    names += "+"
                names += h
                keys.discard(h)
        # 添加剩下的键
        for k in keys:
            if names != "":
                names += "+"
            names += k
        return names


# 热键控制器类
class _HotkeyController:
    # ========================= 【接口】 =========================

    # 添加一组快捷键，对应触发事件为title。 press 为0时按下触发，1抬起触发
    def addHotkey(self, keysName, title, press=0):
        self._start()
        if press != 0 and press != 1:
            return f"[Error] press只能为0按下或1抬起，不能为 {press} 。"
        keySet = _KeyTranslator.names2set(keysName)
        self._hotkeyMutex.lock()
        kl = self._hotkeyList[press]
        for k in kl:  # 检测重复
            if k["keySet"] == keySet:  # 键集合相同
                self._hotkeyMutex.unlock()
                msg = "[Success] 注册事件相同的重复快捷键。"
                if k["title"] != title:  # 事件标题不同
                    msg = f'[Warning] Registering same hotkey. The existing event for {keysName} is {k["title"]}, new event is {title} .'
                return msg
        # 加入列表
        kl.append({"keySet": keySet, "title": title})
        self._hotkeyMutex.unlock()
        return "[Success]"

    # 移除一组快捷键，传入键名或事件之一
    def delHotkey(self, keysName="", title="", press=0):
        if press != 0 and press != 1:
            print(f"[Error] press只能为0按下或1抬起，不能为 {press} 。")
            return
        keySet = _KeyTranslator.names2set(keysName)
        self._hotkeyMutex.lock()
        kListOld = self._hotkeyList[press]  # 旧列表
        kListNew = []  # 新列表
        for k in kListOld:
            # 忽略键集合相同或标题相同
            if (keysName and k["keySet"] == keySet) or (title and title == k["title"]):
                pass
            # 其余键写入新列表
            else:
                kListNew.append(k)
        self._hotkeyList[press] = kListNew
        self._hotkeyMutex.unlock()

    # 开始录制快捷键。过程发送事件为runningTitle，完毕发送事件为finishTitle
    def readHotkey(
        self, runningTitle="<<readHotkeyRunning>>", finishTitle="<<readHotkeyFinish>>"
    ):
        self._start()
        if self._status == 1:
            return (
                "[Warning] Recording is running. 当前快捷键录制已在进行，不能同时录制！"
            )
        self._status = 1
        self._readRunningTitle = runningTitle
        self._readFinishTitle = finishTitle
        return "[Success]"

    # ========================= 【实现】 =========================

    def __init__(self):
        self._listener = None  # 监听器
        # 热键列表，[0]存放按下触发，[1]存放抬起触发
        # 每个元素为：{"keySet":按键集合, "title":事件标题}
        self._hotkeyList = [[], []]
        self._hotkeyMutex = QMutex()  # 热键列表的锁
        self._status = 0  # 状态，0正常，1录制中
        self._pressSet = set()  # 当前已按下的按键集合
        self._strict = True  # 键集合相等的判定，T为严格，F为宽松
        self._ttl = 30  # 长按键超时忽略时间，秒
        self._ttlDict = {}  # 存放当前已按下按键的超时时间
        self._readRunningTitle = ""
        self._readFinishTitle = ""
        # 注册默认监听的热键
        self.addHotkey("esc", "<<esc>>")

    # 第一次注册热键时，启动监听
    def _start(self):
        if not self._listener:
            self._listener = keyboard.Listener(
                on_press=self._onPress, on_release=self._onRelease
            )
            self._listener.start()

    # 按键按下的回调
    def _onPress(self, key):
        keyName = _KeyTranslator.key2name(key)
        # 禁止重复触发
        if keyName in self._pressSet:
            return
        self._checkTTL()  # 检查超时
        self._pressSet.add(keyName)  # 加入集合
        self._ttlDict[keyName] = time() + self._ttl  # 记录超时时间
        if self._status == 0:  # 正常运行
            self._checkKeyEvent(0, keyName)  # 检查按下模式的快捷键
        elif self._status == 1:  # 录制中
            self._readRunning()

    # 按键抬起的回调
    def _onRelease(self, key):
        keyName = _KeyTranslator.key2name(key)
        if not keyName in self._pressSet:
            return
        self._checkTTL()  # 检查超时
        if self._status == 0:  # 正常运行
            self._checkKeyEvent(1, keyName)  # 检查抬起模式的快捷键
        elif self._status == 1:  # 录制结束
            self._readFinish()
        if keyName in self._pressSet:
            self._pressSet.discard(keyName)  # 从集合中删除
            del self._ttlDict[keyName]  # 删除超时时间

    # 检查并触发按键事件
    def _checkKeyEvent(self, press, nowKey):
        # 对比每组按键集合。一致触发，则发送事件
        if self._strict:  # 严格模式，要求完全一致
            for k in self._hotkeyList[press]:
                if k["keySet"] == self._pressSet:
                    PubSubService.publish(k["title"])
        else:  # 宽松模式，只要求当前组合中包含指定按键，且当前按下的按键在指定按键中
            for k in self._hotkeyList[press]:
                if k["keySet"] <= self._pressSet and nowKey in k["keySet"]:
                    PubSubService.publish(k["title"])

    # 更新录制
    def _readRunning(self):
        names = _KeyTranslator.set2names(self._pressSet)
        PubSubService.publish(self._readRunningTitle, names)

    # 录制结束
    def _readFinish(self):
        self._status = 0
        if "esc" in self._pressSet:  # 含esc，则为退出
            PubSubService.publish(self._readFinishTitle, "")
        else:
            names = _KeyTranslator.set2names(self._pressSet)
            PubSubService.publish(self._readFinishTitle, names)

    # 检查已按键的超时时间。若超时，则删除该键
    def _checkTTL(self):
        nowTime = time()
        for k in self._pressSet.copy():
            if nowTime >= self._ttlDict[k]:
                print(f"超时删除 {k}")
                del self._ttlDict[k]
                self._pressSet.discard(k)


HotkeyCtrl = _HotkeyController()
