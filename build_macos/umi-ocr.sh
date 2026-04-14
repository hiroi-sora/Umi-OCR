#!/bin/bash
# Umi-OCR macOS launcher script
# This script is placed at Contents/MacOS/umi-ocr inside the .app bundle.
# It sets up the Python environment and launches the application.

set -e

# Resolve the real path of this script (handles symlinks)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTENTS_DIR="$(dirname "$SCRIPT_DIR")"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

# UmiOCR-data lives inside Resources/
UMIOCR_DATA="${RESOURCES_DIR}/UmiOCR-data"

# Python environment: bundled in Resources/python/ or system Python
if [ -d "${RESOURCES_DIR}/python" ]; then
    # Use bundled Python
    PYTHON="${RESOURCES_DIR}/python/bin/python3"
    export PATH="${RESOURCES_DIR}/python/bin:${PATH}"
    export PYTHONHOME="${RESOURCES_DIR}/python"
else
    # Fallback: use system Python 3
    PYTHON="$(which python3 2>/dev/null || echo /usr/bin/python3)"
fi

# Set the PYSTAND env var so main.py can find the app entry path
export PYSTAND="${SCRIPT_DIR}/umi-ocr"

# Ensure the working directory is UmiOCR-data
cd "${UMIOCR_DATA}"

# Add site-packages to Python path
if [ -d "${UMIOCR_DATA}/site-packages" ]; then
    export PYTHONPATH="${UMIOCR_DATA}/site-packages:${PYTHONPATH:-}"
fi

# Set Qt plugin path for PySide6
PYSIDE6_DIR="${UMIOCR_DATA}/site-packages/PySide6"
if [ -d "${PYSIDE6_DIR}" ]; then
    export QT_PLUGIN_PATH="${PYSIDE6_DIR}/Qt/plugins"
    # Qt5 compat overlay must come BEFORE PySide6 qml path so version 1.x imports resolve first
    QT5_COMPAT="${UMIOCR_DATA}/qt5compat_qml"
    if [ -d "${QT5_COMPAT}" ]; then
        export QML2_IMPORT_PATH="${QT5_COMPAT}:${PYSIDE6_DIR}/Qt/qml"
        export QML_IMPORT_PATH="${QT5_COMPAT}:${PYSIDE6_DIR}/Qt/qml"
    else
        export QML2_IMPORT_PATH="${PYSIDE6_DIR}/Qt/qml"
        export QML_IMPORT_PATH="${PYSIDE6_DIR}/Qt/qml"
    fi
fi

# Use Basic/Fusion style to avoid "native style does not support customization" warnings
# The macOS native style rejects custom backgrounds/contentItems on Controls.
export QT_QUICK_CONTROLS_STYLE="${QT_QUICK_CONTROLS_STYLE:-Fusion}"

# Launch the application
exec "${PYTHON}" "${UMIOCR_DATA}/main.py" "$@"
