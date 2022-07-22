import json

# 配置文件路径
ConfigJsonFile = "Umi-OCR_config.json"

# 配置项
ConfigDict = {
    # 计划任务设置
    "isOpenExplorer": False,  # T时任务完成后打开资源管理器到输出目录。isOutputFile为T时才管用
    "isOpenOutputFile": False,  # T时任务完成后打开输出文件。isOutputFile为T时才管用
    "isOkMission": False,  # T时本次任务完成后执行指定计划任务。
    "okMissionName": "",  # 当前选择的计划任务的name。
    "okMission": {  # 计划任务事件，code为cmd代码
        "关机":
            {"code": 'shutdown /s /t 30 /c "Umi-OCR任务完成，即将关机" /d p:4:1'},
        "休眠":
            {"code": 'shutdown /f /h'},  # shutdown的休眠不能定时
    },

    # 读取剪贴板设置
    "isGlobalHotkey": False,  # T时绑定全局快捷键
    "isNeedCopy": False,  # T时识别完成后自动复制文字
    "globalHotkey": "",  # 全局快捷键

    # 忽略区域设置
    "ignoreArea": None,  # 忽略区域
    # "ignoreAreaPreset": [],  # 忽略区域预设列表

    # 输入文件设置
    "isRecursiveSearch": False,  # T时导入文件夹将递归查找子文件夹中所有图片

    # 输出文件设置
    "isOutputFile": True,  # T时输出内容写入本地文件
    "outputFilePath": "",  # 输出文件目录
    "outputFileName": "",  # 输出文件名称

    # 输出格式设置
    "isOutputDebug": False,  # T时输出调试信息
    "isIgnoreNoText": True,  # T时忽略(不输出)没有文字的图片信息
    "outputStyle": 1,  # 1：纯文本，2：Markdown

    # 识别器设置
    "ocrToolPath": "PaddleOCR-json\PaddleOCR_json.exe",  # 识别器路径
    "imageSuffix": ".jpg .jpe .jpeg .jfif .png .webp .bmp .tif .tiff"  # 图片后缀
}

#  需要保存的设置项
SaveItem = [
    "isOpenExplorer",
    "isOpenOutputFile",
    "okMission",
    "isGlobalHotkey",
    "isNeedCopy",
    "globalHotkey",
    "isRecursiveSearch",
    "isOutputFile",
    "isOutputDebug",
    "isIgnoreNoText",
    "outputStyle",
    "ocrToolPath",
    "imageSuffix",
]


class ConfigModule:

    def initValue(self, optVar):
        """初始化配置。传入并设置tk变量字典"""
        self.optVar = optVar

        def load():
            """从本地json文件读取配置"""
            try:
                with open(ConfigJsonFile, "r", encoding="utf8")as fp:
                    jsonData = json.load(fp)  # 读取json文件
                    for key in jsonData:
                        if key in ConfigDict:
                            ConfigDict[key] = jsonData[key]
            except json.JSONDecodeError:  # 反序列化json错误
                self.save()
            except FileNotFoundError:  # 无配置文件
                self.save()
        load()  # 加载配置文件
        for key in optVar:
            if key in ConfigDict:
                optVar[key].set(ConfigDict[key])

    def isSaveItem(self, key):
        return key in SaveItem

    def save(self):
        """保存配置到本地json文件"""
        saveDict = {}  # 提取需要保存的项
        for key in SaveItem:
            saveDict[key] = ConfigDict[key]
        with open(ConfigJsonFile, "w", encoding="utf8")as fp:
            fp.write(json.dumps(saveDict, indent=4, ensure_ascii=False))

    def update(self, key):
        """更新某个值，从tk变量读取到配置项"""
        ConfigDict[key] = self.optVar[key].get()

    def get(self, key):
        """获取一个配置项的值"""
        return ConfigDict[key]

    def set(self, key, value):
        """设置一个配置项的值"""
        if key in self.optVar:
            self.optVar[key].set(value)
        else:
            ConfigDict[key] = value


Config = ConfigModule()  # 设置模块 单例
