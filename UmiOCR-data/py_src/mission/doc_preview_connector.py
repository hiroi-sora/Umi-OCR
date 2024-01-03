# ===============================================
# =============== 文档预览 - 连接器 ===============
# ===============================================

from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtGui import QPixmap, QImage
import fitz  # PyMuPDF

from .simple_mission import SimpleMission
from ..image_controller.image_provider import PixmapProvider


# 文档预览连接器
class DocPreviewConnector(QObject):
    previewImg = Signal(str)

    def __init__(self, *args):
        super().__init__(*args)
        self._previewMission = SimpleMission(self._previewTask)  # 简单任务对象
        self._previewDoc = None  # 当前预览的对象
        self._previewPath = ""

    @Slot(str, int, str)
    def preview(self, path, page, password):
        page -= 1
        self._previewMission.addMissionList([(path, page, password)])

    def _previewTask(self, msn):
        path, page, password = msn
        if path == self._previewPath:  # 已经加载了
            doc = self._previewDoc
        else:  # 新加载
            try:
                doc = fitz.open(path)
                if doc.isEncrypted and not doc.authenticate(password):
                    msg = "[Warning] isEncrypted"
                    self.previewImg.emit(msg)
                    return
            except Exception as e:
                msg = f"[Error] 打开文档失败：{path} {e}"
                self.previewImg.emit(msg)
                return
            self._previewDoc = doc
            self._previewPath = path
        page_count = doc.page_count
        if page < 0 or page > page_count:
            print(f"[Error] 页数{page}超出范围 0-{page_count} 。")
            return
        pix = doc[page].get_pixmap()
        # 必须先使用变量提取出图像 https://github.com/pymupdf/PyMuPDF/issues/1210
        samples = pix.samples
        qimage = QImage(samples, pix.width, pix.height, QImage.Format_RGB888)
        qpixmap = QPixmap.fromImage(qimage)
        imgID = PixmapProvider.addPixmap(qpixmap)
        self.previewImg.emit(imgID)
