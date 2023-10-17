# =======================================
# =============== 加载插件 ===============
# =======================================

import os
import site
import importlib
from ..ocr.api import initOcrPlugins

# 插件 总目录
PLUGINS_PATH = "plugins"
# 插件组 组名
PLUGINS_GROUPS = ["ocr"]


# 插件控制器
class _PluginsControllerClass:
    def __init__(self):
        self.pluginsDict = {}
        self.optionsDict = {}
        for group in PLUGINS_GROUPS:
            self.pluginsDict[group] = {}
            self.optionsDict[group] = {}

    # 初始化并加载插件
    def init(self):
        # 动态插件
        errors = {}  # 保存失败信息
        # 添加包搜索路径
        if not os.path.exists(PLUGINS_PATH):
            os.makedirs(PLUGINS_PATH)
            print(f"[Error] 插件目录不存在: {PLUGINS_PATH} ")
            return None
        site.addsitedir(PLUGINS_PATH)  # 添加插件搜索路径
        # 加载所有插件。在插件目录中搜索合法的包
        plugList = os.listdir(PLUGINS_PATH)
        for name in plugList:
            initPath = os.path.join(PLUGINS_PATH, name, "__init__.py")
            if os.path.exists(initPath):  # 若包路径下存在 __init__.py ，则尝试加载该包
                flag, res = self._loadPlugin(name)
                if not flag:  # 失败
                    errors[name] = res
                    print(f"[Error] 加载插件 {name} 失败：{res}")
        # TODO: 静态插件
        # 动态插件导入API管理器
        ocrErrs = initOcrPlugins(self.pluginsDict["ocr"])
        if ocrErrs:
            errors.update(ocrErrs)
        return {"options": self.optionsDict, "errors": errors}

    # 加载一个组件python包。成功返回True，失败返回 False, 错误信息
    def _loadPlugin(self, name):
        # 加载包
        try:
            module = importlib.import_module(name)
        except Exception as e:
            return False, f"动态导入包失败：{e}"
        # 验证信息
        if not hasattr(module, "PluginInfo"):
            return False, f"__init__.py 中未定义 PluginInfo 。"
        pluginInfo = module.PluginInfo
        if "group" not in pluginInfo:
            return False, f"__init__.py 中未定义 group 。"
        if "api_class" not in pluginInfo:
            return False, f"__init__.py 中未定义 api_class 。"
        if "global_options" not in pluginInfo:
            pluginInfo["global_options"] = None
        if "local_options" not in pluginInfo:
            pluginInfo["local_options"] = None
        group = pluginInfo["group"]
        if not group or group not in PLUGINS_GROUPS:
            return False, f'__init__.py group "{group}" 不属于已定义的插件类型。'
        # 加载成功、验证成功，则记录信息
        self.pluginsDict[group][name] = pluginInfo
        self.optionsDict[group][name] = {
            "global_options": pluginInfo["global_options"],
            "local_options": pluginInfo["local_options"],
        }
        return True, ""


PluginsController = _PluginsControllerClass()
