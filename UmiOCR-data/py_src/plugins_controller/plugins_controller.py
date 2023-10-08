# =======================================
# =============== 加载插件 ===============
# =======================================

import os
import site
import importlib
from ..ocr.api import initOcrPlugins

OCR_PLUGINS_PATH = "plugins/ocr"

# 插件 总目录
PLUGINS_PATH = "plugins"
# 插件组 目录名
PLUGINS_GROUPS = ["ocr"]


# 插件控制器
class _PluginsControllerClass:
    def __init__(self):
        self.pluginsDict = {}
        for group in PLUGINS_GROUPS:
            self.pluginsDict[group] = {}

    # 初始化并加载插件
    def init(self):
        # 动态插件
        options = {}  # 保存成功加载的插件的配置
        errors = {}  # 保存失败信息
        # 添加包搜索路径
        if not os.path.exists(PLUGINS_PATH):
            print(f"[Error] 插件目录不存在: {PLUGINS_PATH} ")
            return
        site.addsitedir(PLUGINS_PATH)
        for group in PLUGINS_GROUPS:
            options[group] = {}
            plugGroupPath = os.path.join(PLUGINS_PATH, group)
            if not os.path.exists(plugGroupPath):
                print(f"[Error] {plugGroupPath} 插件组目录不存在: {plugGroupPath} ")
                continue
            site.addsitedir(plugGroupPath)
            # 加载所有插件组。在插件组目录中搜索合法的包
            plugList = os.listdir(plugGroupPath)
            for name in plugList:
                initPath = os.path.join(plugGroupPath, name, "__init__.py")
                if os.path.exists(initPath):  # 若包路径下存在 __init__.py ，则尝试加载该包
                    flag, res = self._loadPlugin(group, name)
                    if flag:  # 成功
                        options[group][name] = res
                    else:  # 失败
                        errors[name] = res
                        print(f"[Error] 加载插件 {name} 失败：{res}")
        # TODO: 静态插件
        # 动态插件导入API管理器
        initOcrPlugins(self.pluginsDict["ocr"])
        return {"options": options, "errors": errors}

    # 加载一个组件python包
    def _loadPlugin(self, group, name):
        try:
            module = importlib.import_module(name)
        except Exception as e:
            return False, f"动态导入包失败：{e}"
        if not hasattr(module, "PluginInfo"):
            return False, f"__init__.py 中未定义 PluginInfo"
        pluginInfo = module.PluginInfo
        for i in ["global_options", "local_options", "api_class"]:
            if i not in pluginInfo:
                return False, f"PluginInfo 中未定义 {i}"
        # 加载成功、验证成功，则记录信息
        self.pluginsDict[group][name] = pluginInfo
        opt = {
            "global_options": pluginInfo["global_options"],
            "local_options": pluginInfo["local_options"],
        }
        return True, opt


PluginsController = _PluginsControllerClass()
