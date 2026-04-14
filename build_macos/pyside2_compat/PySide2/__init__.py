# PySide2 → PySide6 compatibility shim for Umi-OCR macOS build.
#
# PySide2 (Qt5) has no wheels for Python 3.12+ or macOS arm64.
# This shim allows the existing codebase (which imports PySide2) to run
# against PySide6 (Qt6) without modifying every import statement.

import PySide6 as _ps6

__version__ = _ps6.__version__
__version_info__ = getattr(_ps6, "__version_info__", __version__)
