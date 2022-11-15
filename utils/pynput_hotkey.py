# 封装 pynput ，提供对外 Hotkey 接口
from pynput import keyboard, mouse
from pynput._util.win32 import KeyTranslator

from time import time

from utils.config import Config


class KeyTranslator_Api:  # 封装 keyTranslator ，负责key、char、vk的转换

    def __init__(self):
        self._kt = KeyTranslator()
        self._layout, _layoutData = self._kt._generate_layout()
        self._normalLayout = _layoutData[(  # 选取常规布局，不受修饰键影响
            False, False, False)]

    def __call__(self, key):
        '''传入pynput的Key对象，返回与修饰键无关的键名char'''
        # 比如，就算按下Shift再按“=”，依然返回“=”而不是“+”
        try:
            if hasattr(key, 'name'):  # 若为控制键
                name = key.name.replace('cmd', 'win')  # win键名称修正
                if '_' in name:  # 清除 _l _r 标记后缀
                    return name.split('_', 1)[0].lower()
                return name.lower()
            else:  # 若为非控制键，通过vk获取键名，避免组合键的char为空
                scan = self._kt._to_scan(key.vk, self._layout)  # vk转扫描码
                char = self._normalLayout[scan][0]  # 扫描码转char
                return char.lower()
        except Exception as e:  # 特殊键（如Fn）没有对应字符，会跳到这里
            # print(f'翻译错误：{e} 事件对象：{key}')
            if key and hasattr(key, 'vk'):
                return f'<{key.vk}>'  # 未知键值，无对应字符，返回键值本身
            else:
                return ''

    def char2vk(self, char):
        '''传入控制键字符串char，返回对应的vk值'''
        if hasattr(keyboard.Key, char):
            vk = getattr(keyboard.Key, char).value
            return vk
        else:  # 非控制键返回自己
            return char


KTA = KeyTranslator_Api()


class Hotkey_Api():  # 热键API，封装 keyboard.Listener

    # 记录一个键按下状态的类
    class Press_Key():

        def __init__(self, keyName):
            self.keyName = keyName
            # TTL：生存时间，秒。一个键按下超过此时间后将忽略它，直到它下次被按下。
            # 这是为了防止意外没有接收到一个键的释放事件，导致它长期留在已按字典里，引起组合键误触。
            self.TTL = 10
            self.updateTTL()

        def updateTTL(self):
            '''刷新生存时间'''
            self.TTL = time()+Config.get('hotkeyMaxTtl')

        def isLive(self, nowTime=None):
            '''若此键仍存活，返回T'''
            if nowTime:
                return nowTime < self.TTL
            return time() < self.TTL

    # 记录一组热键状态的类
    class Hot_Key():

        def __init__(self, hotkey, callback, isPress=True):
            # 通过字符串创建
            if isinstance(hotkey, str):
                self.hotkeyName = hotkey  # 名称
                self.hotkeySet = self.toSet(hotkey)  # 键集合
            # 通过集合创建
            elif isinstance(hotkey, set):
                self.hotkeySet = hotkey  # 键集合
                self.hotkeyName = self.toStr(hotkey)  # 名称
            else:
                raise ValueError(f'不合法的热键值：{hotkey}')
            self.callback = callback  # 回调
            self.isPress = isPress  # T为按压触发，F为释放触发

        @staticmethod
        def toSet(hotkey):
            '''传入热键列表或集合，返回组合键字符串'''
            return set(hotkey.split('+'))

        @staticmethod
        def toStr(hotkeyName):
            '''传入热键名字符串，返回键集'''
            return '+'.join(hotkeyName)

        def isNameEQ(self, hotkeyName):
            '''传入热键字符串，判断是否与本键相等'''
            return self.hotkeySet == self.toSet(hotkeyName)

        def isSetEQ(self, hotkeySet):
            '''传入热键集合，判断是否与本键相等'''
            return self.hotkeySet == hotkeySet

        def isSetSub(self, hotkeySet):
            '''传入热键集合，判断是否包含本键'''
            return self.hotkeySet.issubset(hotkeySet)

        def isKeyIn(self, keyName):
            '''传入单个按键，判断是否在本热键组合内'''
            return keyName in self.hotkeySet

    # ==============================================================

    def __init__(self):
        self.pressDict = {}  # 已按字典
        self.hotkeyList = []  # 热键列表
        # 监听键盘
        self.listener = keyboard.Listener(
            on_press=self._onPress,
            on_release=self._onRelease)
        self.listener.start()
        self.controller = keyboard.Controller()
        self.isReading = False  # 录制模式
        self.readData = {  # 录制信息
            'keyList': [],  # 本组录制的结果
            'keySet': set(),  # 当前等待释放的录制键
            'callback': None  # 录制完成的回调
        }

        # 监听鼠标
        self.mouseListener = None
        self.isMouseListener = False  # 记录鼠标监听器是否在运行
        self.mouseCallback = {'up': None, 'down': None}  # 鼠标回调
        # self.mouseListener.start()
        self.mouseController = mouse.Controller()  # 鼠标操控器

    def join(self):
        '''调试用，键盘监听器运行期间阻塞线程'''
        self.listener.join()

    def _onPress(self, key_):  # 一个键被按下的回调
        self._checkTTL()  # 检查TTL，移除长久没有释放的异常键
        keyName = KTA(key_)  # 键名字符串
        # 维护已按字典
        if keyName not in self.pressDict:  # 按下按键，则加入已按字典
            self.pressDict[keyName] = self.Press_Key(keyName)
        else:   # 此键重复按下（未监听到上次释放），则刷新生存时间
            self.pressDict[keyName].updateTTL()
        # 录制
        if self.isReading:
            if not keyName in self.readData['keyList']:  # 不允许重复录
                self.readData['keyList'].append(keyName)
                self.readData['keySet'].add(keyName)
        # 触发热键
        else:
            self._callHotkey(keyName, True)

    def _onRelease(self, key_):  # 一个键被释放的回调
        self._checkTTL()  # 检查TTL，移除长久没有释放的异常键
        keyName = KTA(key_)  # 键名字符串
        # 录制
        if self.isReading:
            self.readData['keySet'].discard(keyName)  # 删除
            if not self.readData['keySet']:  # 集合为空，所有按下的按键都释放，结束录制
                keyStr = self.Hot_Key.toStr(self.readData['keyList'])
                self.isReading = False
                self.readData['callback'](keyStr)
        # 触发热键
        else:
            self._callHotkey(keyName, False)
        # 维护已按字典
        if keyName in self.pressDict:  # 在已按字典中
            del self.pressDict[keyName]  # 移出已按字典

    def _checkTTL(self):  # 检测已按字典的存活性
        nowTime = time()
        for k, v in list(self.pressDict.items()):
            if not v.isLive(nowTime):
                del self.pressDict[k]

    def _callHotkey(self, key, isPress):  # 检测并触发热键
        nowKeySet = set(self.pressDict.keys())
        debugMsg = f'🖮 {"↓ " if isPress else " ↑"} {key} | {",".join(nowKeySet)}'
        flag = Config.get('isHotkeyStrict')
        for hk in self.hotkeyList:
            if hk.isKeyIn(key) and hk.isPress == isPress:
                # 严格模式，已按集合必须与热键集合完全一致才能触发
                if flag and hk.isSetEQ(nowKeySet):
                    hk.callback()
                    debugMsg += f' | √ {hk.hotkeyName}'
                # 宽容模式，已按集合包含热键集合即可触发
                elif not flag and hk.isSetSub(nowKeySet):
                    hk.callback()
                    debugMsg += f' | √ {hk.hotkeyName}'
        if Config.get('isDebug'):
            print(debugMsg)

    def _addMouseListener(self):

        def _onMouseClick(x, y, button, pressed):  # 鼠标按钮回调
            print(x, y, button, pressed)
            if self.mouseCallback['down'] and pressed:
                self.mouseCallback['down']((x, y))
            elif self.mouseCallback['up'] and not pressed:
                self.mouseCallback['up']((x, y))

        if not self.isMouseListener:
            self.mouseListener = mouse.Listener(on_click=_onMouseClick)
            self.mouseListener.start()
            self.isMouseListener = True

    # ======================= 键盘对外接口 =============================

    def add(self, hotkey, callback, isPress=True):
        '''添加一个快捷键组合监听。按下时调用callback'''
        hotkey = hotkey.lower()  # 转小写
        # 判断重复
        for h in self.hotkeyList:
            if h.isNameEQ(hotkey) and h.callback.__name__ == callback.__name__ \
                    and h.isPress == isPress:
                return
        hk = self.Hot_Key(hotkey, callback, isPress)
        self.hotkeyList.append(hk)

    def addRelease(self, hotkey, callback):
        '''添加一个快捷键组合监听。释放时调用callback'''
        self.add(hotkey, callback, False)

    def remove(self, hotkey):
        '''移除一组快捷键对应的所有监听事件'''
        hset = self.Hot_Key.toSet(hotkey)
        for i in range(len(self.hotkeyList)-1, -1, -1):
            hk = self.hotkeyList[i]
            if hk.isSetEQ(hset):
                del self.hotkeyList[i]

    def isPressed(self, hotkey):
        '''检查当前按键序列是否包含hotkey，是返回T'''
        hset = self.Hot_Key.toSet(hotkey)
        nowKeySet = set(self.pressDict.keys())
        return hset.issubset(nowKeySet)

    def send(self, hotkey):
        '''发送按键序列'''
        keynameList = hotkey.split('+')
        vkList = []
        for name in keynameList:
            name = name.replace('win', 'cmd')
            vk = KTA.char2vk(name)
            vkList.append(vk)
        vks = tuple(vkList)
        with self.controller.pressed(*vks):  # 按需按下和释放
            pass
        # 手动在已按字典中移除
        for name in keynameList:
            if name in self.pressDict:
                del self.pressDict[name]

    def read(self, callback):
        '''录制快捷键。按下并松开一组按键，将按键序列字符串发送到回调函数'''
        if self.isReading:
            callback('', '当前已在录制')
            return
        self.isReading = True
        self.readData['keyList'] = []
        self.readData['keySet'] = set()
        self.readData['callback'] = callback

    # ======================= 鼠标对外接口 =============================

    def addMouseButtonDown(self, callback):
        '''添加一个鼠标按钮监听。按下时调用callback，返回xy坐标元组'''
        self._addMouseListener()
        self.mouseCallback['down'] = callback

    def addMouseButtonUp(self, callback):
        '''添加一个鼠标按钮监听。松开时调用callback，返回xy坐标元组'''
        self._addMouseListener()
        self.mouseCallback['up'] = callback

    def removeMouse(self):
        '''移除鼠标监听'''
        if self.isMouseListener:
            self.mouseListener.stop()
            self.isMouseListener = False
            self.mouseCallback = {'up': None, 'down': None}

    def getMousePos(self):
        return self.mouseController.position


hotkeyApi = Hotkey_Api()
