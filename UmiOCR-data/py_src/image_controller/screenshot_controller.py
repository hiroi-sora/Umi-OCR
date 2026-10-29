# ========================================
# =============== 截图控制 ===============
# ========================================

from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..utils.file_finder import findFiles

import os
import shutil
import subprocess
import tempfile
import time
from PySide2.QtGui import QGuiApplication, QClipboard, QImage, QPixmap  # 截图 剪贴板

Clipboard = QClipboard()  # 剪贴板


# ==================== Wayland 截屏兼容层 ====================
# Wayland 会话下，Qt 的 QScreen.grabWindow() 拿不到屏幕内容：
#   - QT_QPA_PLATFORM=wayland -> 直接返回 0x0 空图
#   - QT_QPA_PLATFORM=xcb     -> 有尺寸但内容全黑（XWayland 看不到 Wayland 窗口）
# 因此改为调用桌面自带的截图工具（KDE Spectacle / 门户）抓整屏，再按屏幕切分。

def _needExternalGrab():
    """当前会话是否需要借助外部工具截屏"""
    try:
        if QGuiApplication.platformName().startswith("wayland"):
            return True
    except Exception:
        pass
    # 平台是 xcb 但存在 Wayland 会话 => 跑在 XWayland 上，抓屏只会得到纯黑
    if os.environ.get("WAYLAND_DISPLAY"):
        return True
    return False


def _grabBySpectacle():
    """用 KDE Spectacle 截取整个桌面，返回 QImage；不可用则返回 None"""
    exe = shutil.which("spectacle")
    if not exe:
        return None
    return _runGrabber([exe, "-b", "-n", "-f", "-o", "{out}"])


def _grabByGrim():
    """用 grim 截取整个桌面（wlroots 系合成器），返回 QImage；不可用则返回 None"""
    exe = shutil.which("grim")
    if not exe:
        return None
    return _runGrabber([exe, "{out}"])


def _grabByGnomeScreenshot():
    """用 gnome-screenshot 截取整个桌面，返回 QImage；不可用则返回 None"""
    exe = shutil.which("gnome-screenshot")
    if not exe:
        return None
    return _runGrabber([exe, "-f", "{out}"])


# 外部截图工具，按优先级排列
_GRABBERS = (_grabBySpectacle, _grabByGrim, _grabByGnomeScreenshot)


def _runGrabber(argv):
    """执行截图命令，把 {out} 换成临时文件路径，返回 QImage 或 None"""
    fd, path = tempfile.mkstemp(prefix="umi_shot_", suffix=".png")
    os.close(fd)
    try:
        subprocess.run(
            [a.replace("{out}", path) for a in argv],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return None
        img = QImage(path)
        if img.isNull():
            return None
        return img
    except Exception:
        return None
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _grabDesktop():
    """依次尝试各外部截图工具，返回第一个成功的整屏 QImage"""
    for grabber in _GRABBERS:
        img = grabber()
        if img is not None:
            return img
    return None


def _cropForScreen(desktopImg, screen, screensList):
    """从整屏图里裁出指定屏幕的区域，返回 QPixmap 或 None"""
    geo = screen.geometry()
    # 虚拟桌面逻辑尺寸（多屏拼接后的大小）
    vw = max([s.geometry().x() + s.geometry().width() for s in screensList] or [0])
    vh = max([s.geometry().y() + s.geometry().height() for s in screensList] or [0])
    if vw <= 0 or vh <= 0:
        return None
    sx = desktopImg.width() / vw
    sy = desktopImg.height() / vh
    x = max(0, int(round(geo.x() * sx)))
    y = max(0, int(round(geo.y() * sy)))
    w = int(round(geo.width() * sx))
    h = int(round(geo.height() * sy))
    w = max(1, min(w, desktopImg.width() - x))
    h = max(1, min(h, desktopImg.height() - y))
    sub = desktopImg.copy(x, y, w, h)
    if sub.isNull() or sub.width() <= 0 or sub.height() <= 0:
        return None
    pixmap = QPixmap.fromImage(sub)
    # 按逻辑像素显示，避免 QML 侧再缩放导致模糊/错位
    if geo.width() > 0:
        pixmap.setDevicePixelRatio(pixmap.width() / geo.width())
    return pixmap


class _ScreenshotControllerClass:

    def getScreenshot(self, wait=0):
        """
        延时wait秒后，获取所有屏幕的截图。返回列表(不为空)，每项为：\n
        {
            "imgID": 图片ID 或 报错信息 "[Error]开头" ,
            "screenName": 显示器名称 ,
            "width": 截图宽度 ,
            "height": 截图高度 ,
        }
        """
        if wait > 0:
            time.sleep(wait)
        try:
            grabList = []
            screensList = QGuiApplication.screens()
            # Wayland 会话：先用外部工具抓一张整屏图
            desktopImg = None
            if _needExternalGrab():
                desktopImg = _grabDesktop()
            for screen in screensList:
                name = screen.name()
                # 获取截图：优先用外部工具的结果，失败则回退 Qt 原生
                pixmap = None
                if desktopImg is not None:
                    pixmap = _cropForScreen(desktopImg, screen, screensList)
                if pixmap is None or pixmap.width() <= 0 or pixmap.height() <= 0:
                    pixmap = screen.grabWindow(0)
                width = pixmap.width()
                height = pixmap.height()
                # 检查截图失败
                if width <= 0 or height <= 0:
                    imgID = f"[Error] width={width}, height={height}"
                # 检查有效，存入提供器，获取imgID
                else:
                    imgID = PixmapProvider.addPixmap(pixmap)
                grabList.append(
                    {
                        "imgID": imgID,
                        "screenName": name,
                        "width": width,
                        "height": height,
                    }
                )
            if not grabList:  # 获取到的截图列表为空
                return [{"imgID": f"[Error] grabList is empty."}]
            return grabList
        except Exception as e:
            return [{"imgID": f"[Error] Screenshot: {e}"}]

    # 对一张图片做裁切。传入原图imgID和裁切参数，返回裁切后的imgID或[Error]
    def getClipImgID(self, imgID, x, y, w, h):
        try:
            pixmap = PixmapProvider.getPixmap(imgID)
            if not pixmap:
                return f'[Error] Screenshot: Key "{imgID}" does not exist in the PixmapProvider dict.'
            if x < 0 or y < 0 or w <= 0 or h <= 0:
                return f"[Error] Screenshot: x/y/w/h value error. {x}/{y}/{w}/{h}"
            pixmap = pixmap.copy(x, y, w, h)  # 进行裁切
            clipID = PixmapProvider.addPixmap(pixmap)  # 存入提供器，获取imgID
            return clipID
        except Exception as e:
            return f"[Error] Screenshot: {e}"

    # 获取当前剪贴板的内容
    # type: imgID paths text
    def getPaste(self):
        # 获取剪贴板数据
        mimeData = Clipboard.mimeData()
        res = {"type": ""}  # 结果字典
        # 检查剪贴板的内容，若是图片，则提取它并扔给OCR
        if mimeData.hasImage():
            image = Clipboard.image()
            pixmap = QPixmap.fromImage(image)
            pasteID = PixmapProvider.addPixmap(pixmap)  # 存入提供器
            res = {"type": "imgID", "imgID": pasteID}
        # 若为URL
        elif mimeData.hasUrls():
            urlList = mimeData.urls()
            paths = []
            for url in urlList:  # 遍历URL列表，提取其中的文件
                if url.isLocalFile():
                    p = url.toLocalFile()
                    paths.append(p)
            paths = findFiles(paths, "image", False)  # 过滤，保留图片的路径
            if len(paths) == 0:  # 没有有效图片
                res = {"type": "error", "error": "[Warning] No image in clipboard."}
            else:  # 将有效图片地址传入OCR，返回地址列表
                res = {"type": "paths", "paths": paths}
        elif mimeData.hasText():
            text = mimeData.text()
            res = {"type": "text", "text": text}
        else:
            res = {"type": "error", "error": "[Warning] Unknow mimeData in clipboard."}
        return res  # 返回结果字典


ScreenshotController = _ScreenshotControllerClass()