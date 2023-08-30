class ApiOcr:
    def start(self, args):  # 启动引擎，或重设参数
        print("未知引擎组件-启动引擎")

    def stop(self):  # 停止引擎
        print("未知引擎组件-停止引擎")

    def runPath(self, imgPath: str):  # 路径识图
        print("未知引擎组件-路径识图")

    def runClipboard(self):  # 剪贴板识图
        print("未知引擎组件-剪贴板识图")

    def runBytes(self, imageBytes):  # 字节流
        print("未知引擎组件-字节流识图")

    def getApiInfo(self):
        print("未知引擎组件-获取额外信息")
        return {}
