#!/bin/bash
# =============================================================
# Umi-OCR macOS Build Script
# =============================================================
#
# Creates a self-contained Umi-OCR.app bundle for macOS.
#
# Usage:
#   ./build_macos/build.sh [--sign IDENTITY] [--python PATH]
#
# Options:
#   --sign IDENTITY   Code-sign with the given Apple Developer identity
#   --python PATH     Path to Python 3 to bundle (default: current python3)
#   --skip-deps       Skip pip install (use existing site-packages)
#
# Output:
#   dist/Umi-OCR.app
#
# Requirements:
#   - macOS 12+ (Monterey)
#   - Python 3.8+
#   - pip
#   - iconutil (ships with Xcode Command Line Tools)

set -euo pipefail

# ── Parse arguments ──────────────────────────────────────────

SIGN_IDENTITY=""
PYTHON_PATH=""
SKIP_DEPS=false
WITH_OCR=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --sign)      SIGN_IDENTITY="$2"; shift 2 ;;
        --python)    PYTHON_PATH="$2"; shift 2 ;;
        --skip-deps) SKIP_DEPS=true; shift ;;
        --with-ocr)  WITH_OCR=true; shift ;;
        *)           echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ── Resolve paths ────────────────────────────────────────────

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${REPO_ROOT}/build_macos"
DIST_DIR="${REPO_ROOT}/dist"
APP_DIR="${DIST_DIR}/Umi-OCR.app"
CONTENTS="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS}/MacOS"
RESOURCES="${CONTENTS}/Resources"

PYTHON="${PYTHON_PATH:-$(which python3)}"

echo "================================================"
echo "  Umi-OCR macOS Build"
echo "================================================"
echo "  Repo:     ${REPO_ROOT}"
echo "  Python:   ${PYTHON}"
echo "  Output:   ${APP_DIR}"
echo "  Sign:     ${SIGN_IDENTITY:-<unsigned>}"
echo "================================================"
echo

# ── Validate ─────────────────────────────────────────────────

if ! command -v "${PYTHON}" &>/dev/null; then
    echo "ERROR: Python not found at ${PYTHON}"
    exit 1
fi

PYTHON_VERSION=$("${PYTHON}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: ${PYTHON_VERSION}"

if ! "${PYTHON}" -c "import sys; assert sys.version_info >= (3, 8), 'Python 3.8+ required'" 2>/dev/null; then
    echo "ERROR: Python 3.8+ is required (found ${PYTHON_VERSION})"
    exit 1
fi

# ── Clean previous build ────────────────────────────────────

echo "Cleaning previous build..."
rm -rf "${APP_DIR}"

# ── Create .app bundle structure ─────────────────────────────

echo "Creating .app bundle structure..."
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES}"

# ── Copy Info.plist ──────────────────────────────────────────

# Read version from about.json and update Info.plist
VERSION=$("${PYTHON}" -c "
import json
with open('${REPO_ROOT}/UmiOCR-data/about.json') as f:
    d = json.load(f)
v = d['version']
s = f\"{v['major']}.{v['minor']}.{v['patch']}\"
if v.get('prerelease'):
    s += f\"-{v['prerelease']}.{v['prereleaseNumber']}\"
print(s)
")
echo "App version: ${VERSION}"

sed -e "s|<string>2.1.5</string>|<string>${VERSION}</string>|g" \
    "${BUILD_DIR}/Info.plist" > "${CONTENTS}/Info.plist"

# ── Create icon (.icns) ─────────────────────────────────────

echo "Creating app icon..."
ICO_FILE="${REPO_ROOT}/UmiOCR-data/qt_res/images/icons/umiocr.ico"
ICONSET_DIR="${DIST_DIR}/umiocr.iconset"

if command -v sips &>/dev/null && command -v iconutil &>/dev/null; then
    # Extract the largest image from the .ico and create iconset
    mkdir -p "${ICONSET_DIR}"

    # Use Python + Pillow to extract icon sizes from .ico
    "${PYTHON}" -c "
from PIL import Image
import os, sys

ico = Image.open('${ICO_FILE}')
iconset = '${ICONSET_DIR}'

# Standard macOS icon sizes
sizes = [16, 32, 64, 128, 256, 512]

for size in sizes:
    try:
        img = ico.copy()
        img = img.resize((size, size), Image.LANCZOS)
        img.save(os.path.join(iconset, f'icon_{size}x{size}.png'))
        # @2x retina version (e.g., icon_16x16@2x.png is 32x32 pixels)
        if size <= 256:
            img2x = ico.copy()
            img2x = img2x.resize((size * 2, size * 2), Image.LANCZOS)
            img2x.save(os.path.join(iconset, f'icon_{size}x{size}@2x.png'))
    except Exception as e:
        print(f'Warning: Could not create {size}x{size} icon: {e}', file=sys.stderr)
" 2>/dev/null

    iconutil -c icns -o "${RESOURCES}/umiocr.icns" "${ICONSET_DIR}" 2>/dev/null && \
        echo "  Created umiocr.icns" || \
        echo "  Warning: iconutil failed, app will use default icon"
    rm -rf "${ICONSET_DIR}"
else
    echo "  Warning: sips/iconutil not found. App will use default icon."
    echo "  Install Xcode Command Line Tools: xcode-select --install"
fi

# ── Copy launcher script ────────────────────────────────────

echo "Installing launcher..."
cp "${BUILD_DIR}/umi-ocr.sh" "${MACOS_DIR}/umi-ocr"
chmod +x "${MACOS_DIR}/umi-ocr"

# Install OCR on-demand installer script
cp "${BUILD_DIR}/install_ocr.command" "${RESOURCES}/install_ocr.command"
cp "${BUILD_DIR}/requirements-ocr.txt" "${RESOURCES}/requirements-ocr.txt"
chmod +x "${RESOURCES}/install_ocr.command"

# ── Copy UmiOCR-data ─────────────────────────────────────────

echo "Copying application data..."
rsync -a --exclude='__pycache__' \
         --exclude='*.pyc' \
         --exclude='.DS_Store' \
         --exclude='logs/' \
         --exclude='temp/' \
         --exclude='temp_doc/' \
         "${REPO_ROOT}/UmiOCR-data/" "${RESOURCES}/UmiOCR-data/"

# ── Install Python dependencies ──────────────────────────────

SITE_PACKAGES="${RESOURCES}/UmiOCR-data/site-packages"

if [ "${SKIP_DEPS}" = false ]; then
    echo "Installing core Python dependencies..."
    "${PYTHON}" -m pip install \
        --target "${SITE_PACKAGES}" \
        --upgrade \
        -r "${BUILD_DIR}/requirements-core.txt" \
        2>&1 | tail -5
    echo "  Core dependencies installed to ${SITE_PACKAGES}"

    if [ "${WITH_OCR}" = true ]; then
        echo "Installing OCR engine dependencies (--with-ocr)..."
        "${PYTHON}" -m pip install \
            --target "${SITE_PACKAGES}" \
            --upgrade \
            -r "${BUILD_DIR}/requirements-ocr.txt" \
            2>&1 | tail -5
        echo "  OCR dependencies installed"
    else
        echo "  OCR engine NOT bundled (lightweight build). Users install via install_ocr.command."
    fi
else
    echo "Skipping dependency installation (--skip-deps)"
fi

# ── Install PySide2 → PySide6 compatibility shim ────────────
# PySide2 has no Python 3.12+ or macOS arm64 wheels, so we use PySide6.
# This shim lets the existing codebase's `from PySide2...` imports work.
echo "Installing PySide2 compatibility shim..."
if [ -d "${SITE_PACKAGES}/PySide2" ]; then
    rm -rf "${SITE_PACKAGES}/PySide2"
fi
cp -R "${BUILD_DIR}/pyside2_compat/PySide2" "${SITE_PACKAGES}/PySide2"
echo "  PySide2 → PySide6 shim installed"

# ── Trim PySide6 (remove unused Qt modules) ──────────────────
# QtWebEngine alone is ~600 MB (Chromium). Remove modules not needed by Umi-OCR.
echo "Trimming PySide6 unused modules..."
PYSIDE6="${SITE_PACKAGES}/PySide6"
TRIM_SIZE_BEFORE=$(du -sm "${PYSIDE6}" | awk '{print $1}')

# Remove development tools
rm -rf "${PYSIDE6}/Assistant.app" "${PYSIDE6}/Designer.app" "${PYSIDE6}/Linguist.app"
rm -rf "${PYSIDE6}/include" "${PYSIDE6}/typesystems" "${PYSIDE6}/glue"

# Remove unused Qt frameworks (keep only what Umi-OCR needs)
QT_LIB="${PYSIDE6}/Qt/lib"
for fw in QtWebEngine QtWebEngineCore QtWebEngineQuick QtWebChannel \
          QtDesigner QtDesignerComponents QtHelp QtSql QtTest \
          Qt3DCore Qt3DRender Qt3DInput Qt3DLogic Qt3DAnimation Qt3DExtras \
          QtQuick3D QtQuick3DRuntimeRender QtQuick3DAssetImport QtQuick3DAssetUtils \
          QtQuick3DParticles QtQuick3DEffects QtQuick3DHelpers QtQuick3DUtils \
          QtGraphs QtCharts QtDataVisualization QtScxml QtStateMachine \
          QtMultimedia QtMultimediaQuick QtSpatialAudio QtSpeech \
          QtSensors QtSerialPort QtSerialBus QtBluetooth QtNfc \
          QtRemoteObjects QtLocation QtPositioning \
          QtVirtualKeyboard QtPdf QtPdfQuick QtTextToSpeech \
          QtQmlCompiler QtLabsAnimation QtCoAP QtMQTT QtOpcUa \
          QtQuickControls2Imagine; do
    rm -rf "${QT_LIB}/${fw}.framework"
done

# Remove unused QML modules
QT_QML="${PYSIDE6}/Qt/qml"
for mod in QtWebEngine QtWebChannel Qt3D QtMultimedia QtSensors QtTest \
           QtLocation QtPositioning QtRemoteObjects QtScxml QtCharts; do
    rm -rf "${QT_QML}/${mod}"
done

TRIM_SIZE_AFTER=$(du -sm "${PYSIDE6}" | awk '{print $1}')
echo "  Trimmed PySide6: ${TRIM_SIZE_BEFORE}M → ${TRIM_SIZE_AFTER}M (saved $((TRIM_SIZE_BEFORE - TRIM_SIZE_AFTER))M)"

# Create QtGraphicalEffects → Qt5Compat/GraphicalEffects symlink for QML compat.
# Qt5 QML code uses "import QtGraphicalEffects 1.15"; Qt6 moved this to Qt5Compat.
QML_DIR="${SITE_PACKAGES}/PySide6/Qt/qml"

# Create QtGraphicalEffects compat module (Qt5 → Qt6 renamed to Qt5Compat.GraphicalEffects)
QGE_DIR="${QML_DIR}/QtGraphicalEffects"
if [ -d "${QML_DIR}/Qt5Compat/GraphicalEffects" ] && [ ! -d "${QGE_DIR}" ]; then
    mkdir -p "${QGE_DIR}"
    # Generate qmldir
    {
        echo "module QtGraphicalEffects"
        for qml in "${QML_DIR}/Qt5Compat/GraphicalEffects/"*.qml; do
            name="$(basename "$qml" .qml)"
            echo "${name} 1.0 ${name}.qml"
            echo "${name} 1.15 ${name}.qml"
        done
    } > "${QGE_DIR}/qmldir"
    # Generate wrapper QML files
    for qml in "${QML_DIR}/Qt5Compat/GraphicalEffects/"*.qml; do
        name="$(basename "$qml" .qml)"
        printf 'import Qt5Compat.GraphicalEffects\n%s {}\n' "${name}" > "${QGE_DIR}/${name}.qml"
    done
    echo "  QtGraphicalEffects compat module created"
fi

# Copy Qt5 compat QML overlays (e.g., FileDialog wrapper for version 1.3 imports)
QT5_COMPAT_SRC="${BUILD_DIR}/qt5compat_qml"
QT5_COMPAT_DST="${RESOURCES}/UmiOCR-data/qt5compat_qml"
if [ -d "${QT5_COMPAT_SRC}" ]; then
    cp -R "${QT5_COMPAT_SRC}" "${QT5_COMPAT_DST}"
    echo "  Qt5 QML compat overlays installed"
fi

# ── Bundle Python interpreter (optional) ─────────────────────

# Create a minimal Python distribution inside the app bundle.
# This makes the .app self-contained — no system Python dependency.
echo "Bundling Python interpreter..."
PYTHON_BUNDLE="${RESOURCES}/python"
PYTHON_REAL="$(${PYTHON} -c "import sys; print(sys.executable)")"
PYTHON_PREFIX="$(${PYTHON} -c "import sys; print(sys.prefix)")"

mkdir -p "${PYTHON_BUNDLE}/bin"
mkdir -p "${PYTHON_BUNDLE}/lib"

# Copy Python binary
cp "${PYTHON_REAL}" "${PYTHON_BUNDLE}/bin/python3"
chmod +x "${PYTHON_BUNDLE}/bin/python3"

# Copy standard library
STDLIB_DIR="$(${PYTHON} -c "import sysconfig; print(sysconfig.get_path('stdlib'))")"
if [ -d "${STDLIB_DIR}" ]; then
    rsync -a --exclude='__pycache__' \
             --exclude='*.pyc' \
             --exclude='test/' \
             --exclude='tests/' \
             --exclude='tkinter/' \
             --exclude='turtledemo/' \
             --exclude='idlelib/' \
             --exclude='site-packages/' \
             --exclude='config-*/' \
             --exclude='distutils/' \
             --exclude='pydoc_data/' \
             --exclude='unittest/' \
             --exclude='_pyrepl/' \
             --exclude='turtle.py' \
             --exclude='doctest.py' \
             --exclude='pydoc.py' \
             "${STDLIB_DIR}/" "${PYTHON_BUNDLE}/lib/python${PYTHON_VERSION}/"
    echo "  Bundled stdlib from ${STDLIB_DIR}"
fi

# Copy lib-dynload (compiled C extensions)
DYNLOAD_DIR="${STDLIB_DIR}/lib-dynload"
if [ -d "${DYNLOAD_DIR}" ]; then
    mkdir -p "${PYTHON_BUNDLE}/lib/python${PYTHON_VERSION}/lib-dynload"
    rsync -a "${DYNLOAD_DIR}/" "${PYTHON_BUNDLE}/lib/python${PYTHON_VERSION}/lib-dynload/"
fi

# Copy all dylibs that Python and its C extensions link against
PYTHON_LIBDIR="$(${PYTHON} -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR') or '')")"
if [ -n "${PYTHON_LIBDIR}" ] && [ -d "${PYTHON_LIBDIR}" ]; then
    # Copy libpython
    for dylib in "${PYTHON_LIBDIR}"/libpython*.dylib; do
        [ -f "$dylib" ] && cp "$dylib" "${PYTHON_BUNDLE}/lib/" && echo "  Bundled $(basename "$dylib")"
    done

    # Find all non-system dylibs referenced by lib-dynload extensions
    echo "  Scanning C extensions for required dylibs..."
    DYNLOAD="${PYTHON_BUNDLE}/lib/python${PYTHON_VERSION}/lib-dynload"
    if [ -d "${DYNLOAD}" ]; then
        # Collect all unique @rpath dylib references from C extensions
        RPATH_LIBS="$(for so in "${DYNLOAD}"/*.so; do
            otool -L "$so" 2>/dev/null
        done | grep '@rpath/' | awk '{print $1}' | sed 's|@rpath/||' | sort -u || true)"

        for libname in ${RPATH_LIBS}; do
            if [ ! -f "${PYTHON_BUNDLE}/lib/${libname}" ]; then
                # Search for the dylib in Python's lib directory, then parent
                FOUND="$(find "${PYTHON_LIBDIR}" -maxdepth 1 -name "${libname}" 2>/dev/null | head -1)"
                if [ -z "${FOUND}" ]; then
                    FOUND="$(find "$(dirname "${PYTHON_LIBDIR}")" -maxdepth 2 -name "${libname}" 2>/dev/null | head -1)"
                fi
                if [ -n "${FOUND}" ] && [ -f "${FOUND}" ]; then
                    cp "${FOUND}" "${PYTHON_BUNDLE}/lib/"
                    echo "  Bundled ${libname}"
                fi
            fi
        done
    fi

    # Add @rpath entry so extensions can find the bundled dylibs
    install_name_tool -add_rpath "${PYTHON_BUNDLE}/lib" "${PYTHON_BUNDLE}/bin/python3" 2>/dev/null || true
fi

# ── Ad-hoc sign all binaries ─────────────────────────────────
# macOS kills binaries with invalid code signatures. After copying,
# the original signatures (from conda, pip, etc.) become invalid.
# Ad-hoc signing makes them loadable without an Apple Developer cert.
# This MUST happen before running the bundled python3 (e.g. ensurepip).
echo "Ad-hoc signing bundled binaries..."
find "${APP_DIR}" -type f \( -name "python3" -o -name "*.dylib" -o -name "*.so" \) \
    -exec codesign --force --sign - {} \; 2>/dev/null
echo "  All binaries signed"

# Bootstrap pip in the bundled Python (must run after ad-hoc signing)
mkdir -p "${PYTHON_BUNDLE}/lib/python${PYTHON_VERSION}/site-packages"
echo "  Bootstrapping pip..."
PYTHONHOME="${PYTHON_BUNDLE}" "${PYTHON_BUNDLE}/bin/python3" -m ensurepip --upgrade 2>&1 | tail -3
if PYTHONHOME="${PYTHON_BUNDLE}" "${PYTHON_BUNDLE}/bin/python3" -c "import pip" 2>/dev/null; then
    echo "  pip installed successfully"
else
    echo "  ERROR: pip bootstrap failed — OCR on-demand install will not work"
fi

echo "  Python bundled at ${PYTHON_BUNDLE}"

# ── Code signing (with developer identity) ───────────────────

if [ -n "${SIGN_IDENTITY}" ]; then
    echo "Code signing with identity: ${SIGN_IDENTITY}"
    codesign --deep --force --verify --verbose \
        --sign "${SIGN_IDENTITY}" \
        --options runtime \
        --entitlements "${BUILD_DIR}/entitlements.plist" \
        "${APP_DIR}"
    echo "  Signed successfully"
    echo
    echo "  To notarize, run:"
    echo "    xcrun notarytool submit dist/Umi-OCR.app.zip --apple-id YOUR_ID --team-id YOUR_TEAM --password YOUR_APP_PASSWORD --wait"
    echo "    xcrun stapler staple dist/Umi-OCR.app"
else
    echo
    echo "NOTE: App is unsigned. Users may need to bypass Gatekeeper:"
    echo "  xattr -cr /Applications/Umi-OCR.app"
fi

# ── Summary ──────────────────────────────────────────────────

APP_SIZE=$(du -sh "${APP_DIR}" | awk '{print $1}')
echo
echo "================================================"
echo "  Build complete!"
echo "  Output: ${APP_DIR}"
echo "  Size:   ${APP_SIZE}"
echo "================================================"
echo
echo "To test:  open dist/Umi-OCR.app"
echo "To create DMG:  ./build_macos/create_dmg.sh"
