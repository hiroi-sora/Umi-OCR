#!/bin/bash
# =============================================================
# Umi-OCR macOS DMG Creator
# =============================================================
#
# Creates a distributable .dmg disk image from the built .app bundle.
#
# Usage:
#   ./build_macos/create_dmg.sh [--notarize]
#
# Prerequisites:
#   - Run build.sh first to create dist/Umi-OCR.app
#
# Output:
#   dist/Umi-OCR-{version}-macOS.dmg

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"
APP_DIR="${DIST_DIR}/Umi-OCR.app"
BUILD_DIR="${REPO_ROOT}/build_macos"
NOTARIZE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --notarize) NOTARIZE=true; shift ;;
        *)          echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ── Validate ─────────────────────────────────────────────────

if [ ! -d "${APP_DIR}" ]; then
    echo "ERROR: ${APP_DIR} not found. Run build.sh first."
    exit 1
fi

# ── Read version ─────────────────────────────────────────────

VERSION=$(defaults read "${APP_DIR}/Contents/Info" CFBundleShortVersionString 2>/dev/null || echo "unknown")

# Detect architecture
ARCH="$(uname -m)"
if [ "${ARCH}" = "arm64" ]; then
    ARCH_LABEL="arm64"
else
    ARCH_LABEL="x86_64"
fi

DMG_NAME="Umi-OCR-${VERSION}-macOS-${ARCH_LABEL}"
DMG_PATH="${DIST_DIR}/${DMG_NAME}.dmg"
DMG_TEMP="${DIST_DIR}/${DMG_NAME}-temp.dmg"

echo "================================================"
echo "  Creating DMG: ${DMG_NAME}.dmg"
echo "  Version:  ${VERSION}"
echo "  Arch:     ${ARCH_LABEL}"
echo "================================================"
echo

# ── Clean previous DMG ──────────────────────────────────────

rm -f "${DMG_PATH}" "${DMG_TEMP}"

# ── Create temporary DMG with app + Applications symlink ─────

STAGING="${DIST_DIR}/dmg-staging"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"

# Hardlink app instead of copying (instant, same disk)
echo "Linking app to staging..."
cp -Rl "${APP_DIR}" "${STAGING}/" 2>/dev/null || {
    echo "  Hardlink failed, falling back to copy..."
    cp -R "${APP_DIR}" "${STAGING}/"
}
echo "  Done."

# Create Applications symlink (standard macOS drag-to-install)
ln -s /Applications "${STAGING}/Applications"

# ── Build DMG ────────────────────────────────────────────────

echo "Creating disk image..."

# Create a read-write DMG first
hdiutil create -volname "Umi-OCR" \
    -srcfolder "${STAGING}" \
    -ov -format UDRW \
    "${DMG_TEMP}"

# Convert to compressed read-only DMG
hdiutil convert "${DMG_TEMP}" \
    -format UDZO \
    -imagekey zlib-level=6 \
    -o "${DMG_PATH}"

# Clean up
rm -f "${DMG_TEMP}"
rm -rf "${STAGING}"

# ── Notarize (optional) ─────────────────────────────────────

if [ "${NOTARIZE}" = true ]; then
    echo
    echo "Submitting for notarization..."
    echo "NOTE: Set these environment variables first:"
    echo "  APPLE_ID        - your Apple ID email"
    echo "  APPLE_TEAM_ID   - your Team ID"
    echo "  APPLE_APP_PWD   - app-specific password"
    echo

    if [ -z "${APPLE_ID:-}" ] || [ -z "${APPLE_TEAM_ID:-}" ] || [ -z "${APPLE_APP_PWD:-}" ]; then
        echo "ERROR: Missing notarization credentials. Set APPLE_ID, APPLE_TEAM_ID, APPLE_APP_PWD."
        exit 1
    fi

    xcrun notarytool submit "${DMG_PATH}" \
        --apple-id "${APPLE_ID}" \
        --team-id "${APPLE_TEAM_ID}" \
        --password "${APPLE_APP_PWD}" \
        --wait

    echo "Stapling notarization ticket..."
    xcrun stapler staple "${DMG_PATH}"
    echo "Notarization complete."
fi

# ── Summary ──────────────────────────────────────────────────

DMG_SIZE=$(du -sh "${DMG_PATH}" | awk '{print $1}')
echo
echo "================================================"
echo "  DMG created successfully!"
echo "  Output: ${DMG_PATH}"
echo "  Size:   ${DMG_SIZE}"
echo "================================================"
