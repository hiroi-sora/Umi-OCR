#!/bin/bash
# =============================================================
# Umi-OCR — Install OCR Engine
# =============================================================
# Double-click this file to install the OCR engine components.
# This downloads RapidOCR + ONNX Runtime (~400 MB).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Resolve paths — this script lives in Contents/Resources/
CONTENTS_DIR="$(dirname "$SCRIPT_DIR")"
RESOURCES_DIR="${SCRIPT_DIR}"
UMIOCR_DATA="${RESOURCES_DIR}/UmiOCR-data"
SITE_PACKAGES="${UMIOCR_DATA}/site-packages"
REQUIREMENTS="${RESOURCES_DIR}/requirements-ocr.txt"

# Find Python
if [ -d "${RESOURCES_DIR}/python" ]; then
    PYTHON="${RESOURCES_DIR}/python/bin/python3"
else
    PYTHON="$(which python3 2>/dev/null || echo /usr/bin/python3)"
fi

echo "================================================"
echo "  Umi-OCR — OCR Engine Installer"
echo "================================================"
echo
echo "  This will install RapidOCR + ONNX Runtime"
echo "  Download size: ~100 MB"
echo "  Installed size: ~400 MB"
echo
echo "  Installing to: ${SITE_PACKAGES}"
echo "  Python: ${PYTHON}"
echo "================================================"
echo

if [ ! -f "${REQUIREMENTS}" ]; then
    echo "ERROR: requirements-ocr.txt not found at ${REQUIREMENTS}"
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

echo "Installing OCR dependencies..."
echo
"${PYTHON}" -m pip install \
    --target "${SITE_PACKAGES}" \
    --upgrade \
    -r "${REQUIREMENTS}"

echo
echo "================================================"
echo "  Installation complete!"
echo "  Please restart Umi-OCR to use OCR features."
echo "================================================"
echo
echo "Press any key to close..."
read -n 1
