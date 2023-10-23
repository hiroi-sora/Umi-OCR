# =======================================
# =============== 二维码页 ===============
# =======================================

from .page import Page  # 页基类
from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..utils.utils import findImages

from PySide2.QtGui import QGuiApplication, QClipboard, QImage, QPixmap  # 截图 剪贴板
import time

Clipboard = QClipboard()  # 剪贴板


class QRcode(Page):
    def __init__(self, *args):
        super().__init__(*args)
