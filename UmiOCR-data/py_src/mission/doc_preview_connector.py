# ===============================================
# =============== 文档预览 - 连接器 ===============
# ===============================================

from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtGui import QPixmap, QImage
import fitz  # PyMuPDF

from .simple_mission import SimpleMission
from ..image_controller.image_provider import PixmapProvider
from ..utils.call_func import CallFunc
from .mission_doc import MissionDOC

MinSize = 0  # 最小渲染分辨率


# 文档预览连接器
class DocPreviewConnector(QObject):
    previewImg = Signal(str)  # imgID
    previewOcr = Signal("QVariant")  # [path, page, res]
    # 注：信号中含多个变量可能导致崩溃？

    def __init__(self, *args):
        super().__init__(*args)
        self._previewMission = SimpleMission(self._previewTask)  # 简单任务对象
        self._previewDoc = None  # 当前预览的对象
        self._previewPath = ""
        self._zooms = {}  # 缓存页面缩放系数

    # 预览PDF画面
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
            self._zooms = {}
        page_count = doc.page_count
        if page < 0 or page > page_count:
            print(f"[Error] 页数{page}超出范围 0-{page_count} 。")
            return
        # 检查页面边长，如果低于阈值，则增加放大系数，以提高渲染清晰度
        rect = doc[page].rect
        w, h = abs(rect[2] - rect[0]), abs(rect[3] - rect[1])
        m = min(w, h)
        if m < MinSize:
            zoom = MinSize / max(m, 1)
            matrix = fitz.Matrix(zoom, zoom)
            self._zooms[page] = zoom
        else:
            matrix = fitz.Identity
            self._zooms[page] = 1
        p = doc[page].get_pixmap(matrix=matrix)
        # 通过 QImage fromImage 转换
        # 必须先使用变量提取出图像 https://github.com/pymupdf/PyMuPDF/issues/1210
        samples = p.samples
        # 必须传入 pix.stride ，否则部分格式的图像会导致崩溃
        qimage = QImage(samples, p.width, p.height, p.stride, QImage.Format_RGB888)
        qpixmap = QPixmap.fromImage(qimage)
        imgID = PixmapProvider.addPixmap(qpixmap)
        self.previewImg.emit(imgID)

    # 预览一页OCR内容
    @Slot(str, int, str, "QVariant")
    def ocr(self, path, page, password, argd):
        argd = argd.toVariant()  # qml对象转python字典
        # if "tbpu.ignoreArea" in argd:  # 删除忽略区域参数
        #     del argd["tbpu.ignoreArea"]

        def _onGet(msnInfo, page_, res):
            # 缩放文本位置
            if page_ in self._zooms and res["code"] == 100:
                z = self._zooms[page_]
                for r in res["data"]:
                    for bi in range(4):
                        r["box"][bi][0] = r["box"][bi][0] * z
                        r["box"][bi][1] = r["box"][bi][1] * z
            page_ += 1
            self.previewOcr.emit([path, page_, res])

        def _onEnd(msnInfo, msg):
            if not msg.startswith("[Success]"):
                res = {"code": 103, "data": msg}
                self.previewOcr.emit([path, -1, res])

        msnInfo = {
            "argd": argd,
            "onGet": _onGet,
            "onEnd": _onEnd,
        }
        MissionDOC.addMission(msnInfo, path, (page, page), password=password)

    # 清空缓存
    @Slot()
    def clear(self):
        self._previewDoc = None
        self._previewPath = ""
