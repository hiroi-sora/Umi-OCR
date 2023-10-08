# ============================================
# =============== OCR API 基类 ===============
# ============================================

"""
调用设计：
每个 OCR API ，同时只会实例化出一个对象。
在不同功能页（如截图OCR、批量OCR）并发异步调用时，
会被任务管理器转化为串行同步调用。
所以API只需要写成同步的形式即可，不需要关心异步的细节。

配置：
每个API具有两个配置组。
    全局配置：
    这是API实例在整个生命期里不变的配置项，如引擎路径，接口key等。
    局部配置：
    这是每组任务可能不一样的配置项，如识别语言。
同时，每个配置组需要在两个地方定义：
    qml中：定义配置内容
    python中：定义映射表，从qml的key映射为python的key
例：
qml配置项：
    "path": {
        "title": qsTr("引擎exe路径"),
        "type": "file",
        "default": "lib/RapidOCR-json/RapidOCR-json.exe",
        "selectExisting": true,
        "selectFolder": false,
        "dialogTitle": qsTr("RapidOCR 引擎exe路径"),
    },
python映射：
    "exe_path": "ocr.RapidOCR.path"

生命期：
初始化 __init__(传入全局配置)
    准备进行一组任务 start(局部配置)
        识图识图识图
        任务结束
    准备进行下一组……
结束实例
"""


class ApiOcr:
    def __init__(self, globalDict):
        self.globalDict = globalDict
        pass

    def start(self, localDict):  # 启动引擎，或重设参数
        print("未知引擎组件-启动引擎")

    def stop(self):  # 停止引擎
        print("未知引擎组件-停止引擎")

    def runPath(self, imgPath: str):  # 路径识图
        print("未知引擎组件-路径识图")

    def runBytes(self, imageBytes):  # 字节流
        print("未知引擎组件-字节流识图")

    def getApiInfo(self):
        print("未知引擎组件-获取额外信息")
        return {}
