# PySide2.QtCore → PySide6.QtCore compatibility shim

from PySide6.QtCore import *  # noqa: F401,F403
from PySide6.QtCore import Qt as _Qt

# In Qt6, these AA_ attributes were removed. The codebase references them
# in run.py and app_opengl.py. We add them as harmless integer stubs so
# QGuiApplication.setAttribute() doesn't crash — Qt6 simply ignores
# unknown attribute values.

# High-DPI scaling is always enabled in Qt6.
if not hasattr(_Qt, "AA_EnableHighDpiScaling"):
    _Qt.AA_EnableHighDpiScaling = 20  # original Qt5 enum value

# OpenGL backend selection was removed in Qt6 (uses RHI abstraction).
if not hasattr(_Qt, "AA_UseDesktopOpenGL"):
    _Qt.AA_UseDesktopOpenGL = 15
if not hasattr(_Qt, "AA_UseOpenGLES"):
    _Qt.AA_UseOpenGLES = 16
if not hasattr(_Qt, "AA_UseSoftwareOpenGL"):
    _Qt.AA_UseSoftwareOpenGL = 17

# AA_ShareOpenGLContexts may still exist in some PySide6 builds.
if not hasattr(_Qt, "AA_ShareOpenGLContexts"):
    _Qt.AA_ShareOpenGLContexts = 18
