# ===============================================
# =============== OCR 插件接口管理 ===============
# ===============================================

ApiDict = {}


# TODO: 静态插件
# 由插件控制器调用，初始化OCR插件的接口。传入动态插件
def initOcrPlugins(plugins):
    global ApiDict
    for p in plugins:
        ApiDict[p] = plugins[p]["api_class"]


# 生成一个ocr api实例，成功返回对象，失败返回 [Error] 开头的字符串
def getApiOcr(apiKey, argd):
    # 检测argd，恢复int类型
    for k in argd:
        n = argd[k]
        if isinstance(n, float):
            rounded = round(n)
            if abs(n - rounded) <= 1e-7:
                argd[k] = rounded
    if apiKey in ApiDict:
        try:
            return ApiDict[apiKey](argd)  # 实例化后返回
        except Exception as e:
            print(f"生成api实例{apiKey}失败：{e}")
            return str(e)
    return f'[Error] "{apiKey}" not in ApiDict.'
