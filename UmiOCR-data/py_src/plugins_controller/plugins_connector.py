# =============================================
# =============== 插件管理连接器 ===============
# =============================================

from PySide2.QtCore import QObject, Slot, Signal

from .plugins_controller import PluginsController


# 插件连接器
class PluginsConnector(QObject):
    # 初始化插件，返回字典：
    # {"options": ["ocr":{"key":成功加载的插件的配置}], "errors": {"key": "失败信息"} }
    @Slot(result="QVariant")
    def init(self):
        return PluginsController.init()
