# PySide2.QtGui → PySide6.QtGui compatibility shim

from PySide6.QtGui import *  # noqa: F401,F403
from PySide6.QtGui import QClipboard as _QClipboard6, QGuiApplication


class QClipboard:
    """PySide2 compatibility wrapper for QClipboard.

    In PySide2, ``QClipboard()`` could be called directly at module level.
    PySide6 forbids direct construction — you must use
    ``QGuiApplication.clipboard()``.  This wrapper defers to the real
    clipboard instance lazily, so existing ``Clipboard = QClipboard()``
    code keeps working.
    """

    def __init__(self):
        self._real = None

    def _clipboard(self):
        if self._real is None:
            app = QGuiApplication.instance()
            if app is not None:
                self._real = app.clipboard()
        return self._real

    def __getattr__(self, name):
        cb = self._clipboard()
        if cb is not None:
            return getattr(cb, name)
        raise RuntimeError(
            "QClipboard accessed before QGuiApplication is created"
        )
